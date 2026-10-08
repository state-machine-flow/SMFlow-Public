# Standalone Automotive Power Window Controller Module (WCM)

An industry reference implementation of an electronic Power Window Control Module (WCM) for automotive retrofits, classic muscle car restomods, custom truck repowers, and commercial vehicle body electronics.

Designed to replace manual crank windows or crude aftermarket toggle switch kits with modern OEM-grade window automation: momentary manual travel, one-touch express up/down, FMVSS 118 compliant anti-pinch safety reversal, mechanical end-stop stall detection, and ignition-off Retained Accessory Power (RAP) with door cancel.

Targeted for the **Raspberry Pi Pico (`rp2040-pico`)** and verifiable in the **SMFlow Simulator (`simulator`)**.

---

## 1. Application Scope & The Retrofit Problem

Upgrading classic and custom vehicles (e.g. Chevy C10 / K5 Blazer, Ford Bronco / F-Series, muscle cars, kit cars) to power windows introduces significant comfort and safety challenges when using standard aftermarket toggle switch kits:

1. **Extreme Pinch Hazard**: A typical 12V permanent magnet window regulator generates between **300 N and 450 N (70 to 100 lbf)** of pinching force. Without electronic current sensing and automated reversal, an ascending window can easily crush fingers or cause severe injury to children and pets.
2. **Distracted Driving from Holding Switches**: Without one-touch express capability, the driver must take a hand off the steering wheel and hold a switch for 4 to 6 seconds while merging, exiting parking structures, or entering toll gates.
3. **Switch Contact & Motor Burnout**: Aftermarket manual switches lack current-limiting stall detection. When the window hits the hard mechanical stop at the top or bottom, holding the switch forces locked-rotor current (> 20 A to 30 A) through the motor brushes and relay contacts, burning them out.
4. **Stranded Windows on Engine Shutdown**: Turning off the ignition key instantly kills 12V power in vintage wiring harnesses, forcing the driver to turn the ignition key back on to close windows.

The SMFlow **Power Window Controller** addresses these requirements with deterministic 10 ms cycle times, precise analog current sensing, and robust state machines compiled ahead of time to native C++.

---

## 2. System Architecture & Control Strategy

```
+-----------------------------------------------------------------------------------------+
|                        SMFlow Power Window Controller (RP2040 Pico)                     |
|                                                                                         |
|   [ Ignition (+12V Key) ] --------> GP14 (DI) --+                                       |
|                                                 +--> [ 30s RAP Timer & Door Cancel ]    |
|   [ Door Ajar Switch ] -----------> GP15 (DI) --+            │                          |
|                                                              ▼                          |
|   [ Window UP Switch ] -----------> GP16 (DI) -----> [ Tap vs Hold Timing (350ms) ]     |
|   [ Window DOWN Switch ] ---------> GP17 (DI) -----> [ Express Latches & Abort ]        |
|                                                              │                          |
|   [ Motor Current Shunt ] --------> GP26 (AI) -----> [ Current Window Comparators ]     |
|                                                              │                          |
|                                                 +--> [ Anti-Pinch Reversal (1.0s DOWN)] |
|                                                 +--> [ Stall Filter (100ms >= 10.0A) ]  |
|                                                 +--> [ Max Travel Watchdog (8.0s) ]     |
|                                                 ▼                                       |
|   [ Motor UP Driver / Relay ] <---- GP18 (DO) <---- [ Interlocked UP Output Gate ]      |
|   [ Motor DOWN Driver / Relay ] <-- GP19 (DO) <---- [ Interlocked DOWN Output Gate ]    |
|   [ Dash Pinch MIL Warning ] <----- GP20 (DO) <---- [ Safety Reversal Alarm Output ]    |
+-----------------------------------------------------------------------------------------+
```

### Actuator Outputs & Safety Features

- **MotorUp (GP18)**:
  - Commands the H-bridge high-side driver or 30 A Form-C relay to drive the window motor upwards.
  - Automatically locked out if DOWN is active, if end-stop stall is detected, or if anti-pinch has tripped.
- **MotorDown (GP19)**:
  - Commands the H-bridge high-side driver or 30 A Form-C relay to drive the window motor downwards.
  - Automatically forced active for 1.0 second during an anti-pinch obstruction event.
- **PinchAlarm (GP20)**:
  - Digital output illuminating an instrument cluster MIL or driving an audible chime during an anti-pinch safety reversal.

---

## 3. Calibrated Setpoints & Parameters

| Parameter Variable / Timer | Calibrated Value | Function |
| :--- | :---: | :--- |
| `PinchCurrentThreshold` | **6.5 A** | Current threshold where obstruction detection begins (normal running: 2.5–4.0 A). |
| `StallCurrentThreshold` | **10.0 A** | Locked-rotor stall threshold indicating mechanical end of travel (top or bottom). |
| `timer_hold_up` / `down` | **350 ms** | Tap vs hold boundary: < 350 ms = One-Touch Express; >= 350 ms = Manual Momentary. |
| `timer_reversal` | **1,000 ms (1.0s)**| Downward safety reversal drive duration under FMVSS 118 (~100 mm window opening). |
| `timer_stall_filter` | **100 ms** | De-glitch filter ensuring motor startup inrush (50–80 ms) does not trigger false stall trips. |
| `timer_max_travel` | **8,000 ms (8.0s)**| Safety watchdog timeout halting drive if regulator binds or current sensor disconnects. |
| `timer_rap` | **30,000 ms (30.0s)**| Retained Accessory Power grace period maintaining window power after key-off. |

---

## 4. Control Logic & Operating Modes

### 1. Momentary Manual Operation (Hold >= 350 ms)
- When the driver presses and holds either `Up` or `Down` for longer than 350 ms:
- The motor runs continuously in the requested direction.
- The instant the switch is released, motor drive ceases immediately.

### 2. One-Touch Express Operation (Tap < 350 ms)
- A brief tap on the switch (< 350 ms) latches Express mode (`latch_express_up` or `latch_express_down`).
- The window glides automatically to its full mechanical limit without requiring the driver to hold the switch.
- **Tap-to-Abort**: Tapping the opposite switch while Express motion is active cancels automated travel immediately.

### 3. FMVSS 118 Anti-Pinch Protection & Automated Safety Reversal
- During upward motion, the analog motor shunt current is continuously sampled at 100 Hz.
- If an obstruction (e.g. child's hand, arm, or object) is trapped between the glass and window frame, motor current rises into the **6.5 A to 10.0 A** band.
- `gate_pinch_detected` trips instantly, immediately de-energizing `MotorUp`.
- The controller activates `timer_reversal` (TOF 1.0s), forcing `MotorDown` ON for exactly **1.0 second** (~100 mm of window opening) to release the trapped object.
- `PinchAlarm` illuminates on the dashboard.
- Express UP is locked out until the driver manually operates the Down switch.

### 4. End-Stop Mechanical Stall Detection
- When the glass reaches the mechanical hard stop at full top or full bottom:
- Motor current spikes to locked-rotor stall (**>= 10.0 A**).
- After a 100 ms confirmation filter (`timer_stall_filter`), `not_stall` drops false, halting motor drive instantly.
- This prevents motor brush overheating, regulator cable stretch, and battery drain.

### 5. Retained Accessory Power (RAP) & Door-Open Cancel
- When the driver turns off the ignition key (`Ignition == false`):
- An auxiliary power timer (`timer_rap`) keeps the windows functional for **30.0 seconds**, allowing passengers to close windows after parking.
- **Door Cancel**: If any door is opened (`DoorOpen == true`) while the ignition is off, RAP terminates immediately, preventing battery discharge and securing the vehicle against unauthorized access.
- Cycling the ignition key back ON restores power immediately.

### 6. H-Bridge Electrical Interlock
- Software cross-interlocking ensures `MotorUp` and `MotorDown` can never be energized concurrently, preventing H-bridge shoot-through damage and Form-C relay short circuits.

---

## 5. Multi-Window Modular Architecture

The reference flow `power-window-controller.smflow` provides the complete control engine for a single window. In automotive vehicle applications, this flow scales in two standard ways:

### 5.1 Central 4-Window Controller Architecture
To control all four windows in a 4-door vehicle from a single central module (e.g. Arduino Opta or custom RP2040 board):
- Replicate the window logic core four times:
  - `Window_FL` (Front Left - Driver)
  - `Window_FR` (Front Right - Passenger)
  - `Window_RL` (Rear Left)
  - `Window_RR` (Rear Right)
- **Master Lockout Switch**: Add a single master lockout digital input (`WindowLockout`) that disables passenger and rear local switches while keeping driver master switches active.
- **Shared RAP & Current Shunt**: All four window channels share the same `timer_rap` and door ajar logic.

### 5.2 Distributed Door Module Architecture (CAN / LIN Nodes)
In modern automotive architectures, an identical instance of `power-window-controller.smflow` runs in a micro-PLC inside each door panel, sharing ignition state and master lockout commands over a CAN or LIN bus.

---

## 6. Hardware Wiring & Pinout Specification

### Raspberry Pi Pico (`rp2040-pico`) Pinout

| Signal Name | Direction | Pico Pin | Electrical Conditioning | Description |
| :--- | :---: | :---: | :--- | :--- |
| `Ignition` | DI | **GP14** | +12V switched via 10k/3.3k divider + 3.3V Zener | Vehicle ignition RUN/ACC line |
| `DoorOpen` | DI | **GP15** | Frame switch via 10k/3.3k divider (True = Open) | Door ajar courtesy switch |
| `Up` | DI | **GP16** | Stalk/Console switch via 10k/3.3k divider | Window UP switch contact |
| `Down` | DI | **GP17** | Stalk/Console switch via 10k/3.3k divider | Window DOWN switch contact |
| `MotorCurrent` | AI | **GP26** | 0–3.3V analog input from INA180 shunt amplifier | DC motor current (0.0 A to 15.0 A) |
| `MotorUp` | DO | **GP18** | 3.3V logic -> N-MOSFET gate -> Form-C 30A Relay | Motor UP relay coil (+12V) |
| `MotorDown` | DO | **GP19** | 3.3V logic -> N-MOSFET gate -> Form-C 30A Relay | Motor DOWN relay coil (+12V) |
| `PinchAlarm` | DO | **GP20** | 3.3V logic -> Low-side driver -> Dash MIL | Cluster anti-pinch fault warning lamp |

---

## 7. Simulation & Verification

The test suite in `power-window-controller.smtest` asserts all functional operating modes, timing boundaries, anti-pinch reversal, and RAP behavior.

### Validating the Flow

```bash
smflow validate samples/reference/automotive/power-window-controller/power-window-controller.smflow
smflow validate samples/reference/automotive/power-window-controller/power-window-controller.smflow --target rp2040-pico
smflow validate samples/reference/automotive/power-window-controller/power-window-controller.smflow --target simulator
```

### Running Interactive Simulation

```bash
smflow simulate samples/reference/automotive/power-window-controller/power-window-controller.smflow
```

Inside the simulator:
```text
set Ignition true
set DoorOpen false
set MotorCurrent 3.0
set Up true
step 1
dump
```

Observe that `MotorUp` is `true`, while `MotorDown` and `PinchAlarm` are `false`.

Simulate an anti-pinch obstruction event:
```text
set MotorCurrent 7.5
step 1
dump
```

Observe that `MotorUp` turns `false` immediately, while `MotorDown` and `PinchAlarm` turn `true` (automated 1.0s safety reversal).

---

## 8. Production Build & Deployment

To compile the power window controller for physical deployment on a Raspberry Pi Pico:

```bash
# Compile native C++ firmware sketch
smflow build samples/reference/automotive/power-window-controller/power-window-controller.smflow --target rp2040-pico

# Deploy directly over USB (board in BOOTSEL mode or connected via serial COM port)
smflow deploy samples/reference/automotive/power-window-controller/power-window-controller.smflow --target rp2040-pico
```
