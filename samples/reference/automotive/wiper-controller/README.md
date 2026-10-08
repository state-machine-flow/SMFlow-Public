# Automotive Windshield Wiper Controller (WCM)

An industry reference implementation of an electronic Windshield Wiper Control Module (WCM) for automotive retrofits, restomods, commercial truck repowers, and aftermarket body control electronics.

Designed for modernizing classic muscle cars, vintage trucks, hot rods, and kit vehicles with full-featured wiper automation: multi-speed continuous wiping, timed intermittent mode with immediate first-wipe response, coordinated washer pump fluid management with post-wash drip clearing cycles, automatic park switch cam detection, ignition-off park rundown, and dual watchdog stall protection.

Targeted for the **Raspberry Pi Pico (`rp2040-pico`)** and verifiable in the **SMFlow Simulator (`simulator`)**.

---

## 1. Application Scope & The Automotive Wiper Problem

In automotive body electronics, windshield wiper systems appear simple to the vehicle operator, but present subtle electromechanical and safety requirements:

1. **Mechanical Cam Synchronization**: The wiper motor gearbox contains an internal mechanical cam disc switch (`ParkSwitch`). If motor power is interrupted at an arbitrary instant when the driver switches the stalk OFF, the wiper blades freeze immediately in the driver's forward sightline. The controller must sense the mechanical park cam and maintain power until the wiper arms have cleanly completed their sweep and settled at the bottom of the windshield cowl.
2. **Dual-Winding High/Low Interlock**: Automotive two-speed permanent magnet wiper motors utilize separate brushes on the commutator (typically a low-speed brush at 180° and an advanced high-speed brush at ~120°). Energizing both low-speed and high-speed windings simultaneously creates high internal circulating currents across the commutator, overheating brushes and damaging the armature. Strict electrical and logical interlocking is essential.
3. **Ignition-Off Park Rundown**: When a driver turns the ignition key OFF while wipers are mid-sweep across the glass, classic vehicle wiring abruptly cuts 12V power, stranding the blades vertically. Modern automotive standards require an automatic ignition-off rundown circuit that retains low-speed power for several seconds until the blades finish their stroke and reach the park rest position.
4. **Stall & Frozen Blade Protection**: In winter conditions, wiper blades frequently freeze to the glass with ice, or heavy snow loads jam the linkage. In a locked-rotor condition, the motor draws between 20 A and 35 A continuous current. Sustained stall current quickly melts plastic worm gears, welds relay contacts, and creates an under-dash fire hazard. Dual watchdog stall timers must detect motion failure (both out of park and stuck at park) and isolate all motor circuits within seconds.
5. **Washer Fluid & Drip Cycle Coordination**: Spraying washer fluid requires coordinating the washer pump motor with low-speed wiper sweeps, followed by a calibrated post-spray drip wipe sequence after the washer stalk is released to remove fluid streaks and gravity drips.

The SMFlow **Wiper Controller** implements these behaviors in a deterministic 10 ms control loop compiled directly to native C++.

---

## 2. System Architecture & Control Strategy

```
+-----------------------------------------------------------------------------------------+
|                        SMFlow Wiper Controller (RP2040 Pico)                             |
|                                                                                         |
|   [ Ignition (+12V Key) ] --------> GP14 (DI) --+                                       |
|                                                 +--> [ 5.0s Ignition-Off Rundown ]      |
|   [ Park Switch (Gearbox Cam) ] --> GP15 (DI) -----> [ Park Cam & Edge Detection ]      |
|                                                              │                          |
|   [ Wiper Low Stalk Switch ] -----> GP16 (DI) --+            │                          |
|   [ Wiper High Stalk Switch ] ----> GP17 (DI) --+--> [ Mode Arbitration & Interlock ]    |
|   [ Intermittent Switch ] --------> GP18 (DI) -----> [ 4.0s INT Pause Timer & Latch ]   |
|   [ Washer Stalk Switch ] --------> GP19 (DI) -----> [ 3.0s Post-Wash Drip TOF ]        |
|                                                              │                          |
|                                                 +--> [ Dual Stall Watchdog Timers ]     |
|                                                 │    (10s Moving Stall / 5s Park Stall) |
|                                                 ▼                                       |
|   [ Low-Speed Wiper Relay ] <------ GP20 (DO) <---- [ Low-Speed Arbitration Gate ]      |
|   [ High-Speed Wiper Relay ] <----- GP21 (DO) <---- [ High-Speed Interlocked Gate ]     |
|   [ Washer Fluid Pump Relay ] <---- GP22 (DO) <---- [ Washer Output Gate ]              |
|   [ Dash Wiper MIL / Fault ] <----- GP26 (DO) <---- [ Latched Safety Cutoff Lamp ]      |
+-----------------------------------------------------------------------------------------+
```

### Staged Actuator Architecture

- **WiperMotorLow (GP20)**:
  - Drives a 40 A automotive relay powering the low-speed wiper motor brush (~45 wipes/min).
  - Used for continuous low mode, intermittent wipe cycles, washer drip wipe sequences, and auto-park rundown.
  - Automatically locked out whenever High speed is active.
- **WiperMotorHigh (GP21)**:
  - Drives a 40 A automotive relay powering the high-speed wiper motor brush (~65 wipes/min).
  - Used for continuous high mode in heavy rain.
  - Overrides Low speed, Intermittent mode, and washer wipe commands.
- **WasherPump (GP22)**:
  - Drives a 20 A automotive relay powering the 12V windshield washer fluid reservoir pump.
  - Active only while the washer stalk is held, ignition is ON, and no fault is latched.
- **FaultIndicator (GP26)**:
  - Illuminates instrument cluster wiper MIL or dashboard fault indicator upon stall timeout trip.

---

## 3. Calibrated Setpoints & Operating Modes

| Parameter / Timer | Calibrated Value | Function |
| :--- | :---: | :--- |
| `timer_int_delay` | **4,000 ms (4.0s)** | Pause dwell time between consecutive intermittent wipe cycles. |
| `timer_wash_drip` | **3,000 ms (3.0s)** | Post-wash drip wipe duration after releasing washer stalk. |
| `timer_ign_rundown`| **5,000 ms (5.0s)** | Maximum power hold window to park moving blades after key-off. |
| `timer_run_stall` | **10,000 ms (10.0s)**| Watchdog timeout detecting blades moving without reaching park (jammed sweep). |
| `timer_park_stall`| **5,000 ms (5.0s)** | Watchdog timeout detecting motor commanded while stuck at park (frozen blades). |

---

## 4. Control Logic & Operating States

### 1. Off / Parked State (`Ignition == false` or Stalk OFF, Blades at Park)
When the vehicle ignition is OFF or all stalk switches are in their neutral OFF position with blades resting in the cowl:
- All outputs are de-energized.
- Quiescent current draw is negligible (< 100 µA).

### 2. Continuous Low Speed Mode (`Low == true`, `High == false`)
- `WiperMotorLow` energizes continuously at ~45 wipes/minute.
- `WiperMotorHigh` and `WasherPump` remain OFF.

### 3. Continuous High Speed Mode (`High == true`)
- `WiperMotorHigh` energizes continuously at ~65 wipes/minute.
- Hardware/software interlocking de-energizes `WiperMotorLow`.
- Even if the driver leaves the Low switch active or pulls the washer stalk, High speed maintains sole authority over motor drive.

### 4. Intermittent Mode (`Intermittent == true`, Low/High OFF)
- **Immediate Initial Wipe**: Selecting the INT switch generates a rising-edge trigger (`edge_int_start`), immediately launching an initial wipe cycle so the driver sees immediate windshield clearing.
- **Wipe Cycle Latch**: The cycle latch (`latch_int_wipe`) holds `WiperMotorLow` ON as the blades sweep across the windshield.
- **Park Reset**: When the blades complete the sweep and return to the cowl, the rising edge of `ParkSwitch` (`edge_park_rise`) resets the cycle latch, stopping the motor.
- **4.0-Second Dwell**: While stationary at park, `timer_int_delay` times a 4.0-second delay. When the timer expires, `edge_int_timer` triggers the next wipe cycle.

### 5. Washer Fluid & Post-Wash Drip Wipes (`Washer == true`)
- Pulling the washer stalk immediately activates `WasherPump` and begins sweeping wipers in low speed (`WiperMotorLow`).
- Releasing the stalk de-energizes `WasherPump` instantly to avoid fluid wastage.
- An off-delay timer (`timer_wash_drip`, TOF 3.0s) keeps `WiperMotorLow` energized for an additional 3.0 seconds, completing 2–3 clearing sweeps to eliminate fluid streaks and drips.
- When the 3.0-second timer expires, auto-park logic completes the final stroke and stops blades cleanly at park.

### 6. Auto-Park Detection (Switching OFF Mid-Sweep)
- When the driver switches off the stalk from Low, High, Intermittent, or Washer while blades are mid-windshield (`ParkSwitch == false`):
- `gate_park_rundown` senses `not_parked` and maintains `WiperMotorLow` active.
- As soon as the mechanical cam switch closes (`ParkSwitch == true`), power to the motor is cut instantly, ensuring blades always park at the base of the windshield.

### 7. Ignition-Off Park Rundown (`Ignition` switched OFF Mid-Sweep)
- If the driver turns off the ignition key while wipers are in motion on the glass:
- Normal user controls are isolated immediately.
- `timer_ign_rundown` maintains a 5.0-second post-shutdown power window.
- `gate_park_rundown` continues driving the motor in low speed until `ParkSwitch == true`.
- Once parked, motor power is disconnected. If blades were already parked when the key was turned off, outputs remain off.

### 8. Dual Watchdog Stall Protection (Fault Timeout)
- **Running Stall**: If the motor is running while blades are out of park for more than **10.0 seconds** without touching the park switch (e.g. heavy snow accumulation or mechanical linkage failure), `timer_run_stall` trips the safety fault latch (`latch_fault`).
- **Park Stall**: If the motor is commanded to run from park, but blades remain stuck in park for more than **5.0 seconds** (e.g. blades frozen to the windshield by ice), `timer_park_stall` trips `latch_fault`.
- **Fault Shutdown**: When `latch_fault` trips:
  - All motor outputs (`WiperMotorLow`, `WiperMotorHigh`) are immediately de-energized to protect windings and wiring harnesses from thermal destruction.
  - `WasherPump` is disabled.
  - `FaultIndicator` illuminates on the instrument cluster.
  - The system remains safely locked out until the driver cycles the vehicle ignition key OFF and back ON (`not_ign` resets `latch_fault`).

---

## 5. Hardware Interface & Wiring Specification

### 5.1 Raspberry Pi Pico (`rp2040-pico`) Pinout

| Signal Name | Direction | Pico Pin | Electrical Specification | Description |
| :--- | :---: | :---: | :--- | :--- |
| `Ignition` | DI | **GP14** | +12V switched via 10k/3.3k divider + 3.3V Zener | Vehicle ignition RUN/ACC line |
| `ParkSwitch` | DI | **GP15** | Gearbox cam switch via 10k/3.3k divider | True = Blades resting at park position |
| `Low` | DI | **GP16** | Stalk Low switch via 10k/3.3k divider | Continuous Low speed request |
| `High` | DI | **GP17** | Stalk High switch via 10k/3.3k divider | Continuous High speed request |
| `Intermittent` | DI | **GP18** | Stalk INT switch via 10k/3.3k divider | Timed intermittent mode request |
| `Washer` | DI | **GP19** | Stalk Wash switch via 10k/3.3k divider | Momentary washer fluid spray request |
| `WiperMotorLow` | DO | **GP20** | 3.3V logic -> N-MOSFET gate -> 40A Relay coil | Low-speed wiper motor brush (+12V) |
| `WiperMotorHigh`| DO | **GP21** | 3.3V logic -> N-MOSFET gate -> 40A Relay coil | High-speed wiper motor brush (+12V) |
| `WasherPump` | DO | **GP22** | 3.3V logic -> N-MOSFET gate -> 20A Relay coil | Washer fluid reservoir pump (+12V) |
| `FaultIndicator`| DO | **GP26** | 3.3V logic -> Low-side driver -> Dash MIL | Cluster wiper fault / stall warning lamp |

---

## 6. Simulation & Verification

The test suite in `wiper-controller.smtest` asserts all functional operating modes, timing intervals, interlocks, auto-park detection, ignition-off rundown, and stall watchdogs.

### Validating the Flow

```bash
smflow validate samples/reference/automotive/wiper-controller/wiper-controller.smflow
smflow validate samples/reference/automotive/wiper-controller/wiper-controller.smflow --target rp2040-pico
smflow validate samples/reference/automotive/wiper-controller/wiper-controller.smflow --target simulator
```

### Running Interactive Simulation

```bash
smflow simulate samples/reference/automotive/wiper-controller/wiper-controller.smflow
```

Inside the simulator:
```text
set Ignition true
set ParkSwitch true
set Low true
step 1
dump
```

Observe that `WiperMotorLow` is `true`, while `WiperMotorHigh`, `WasherPump`, and `FaultIndicator` are `false`.

Simulate moving the blades out of park:
```text
set ParkSwitch false
set Low false
step 1
dump
```

Observe that `WiperMotorLow` remains `true` (auto-park rundown keeps motor running).

Simulate blades arriving at the park rest position:
```text
set ParkSwitch true
step 1
dump
```

Observe that `WiperMotorLow` turns `false` immediately as park is reached.

---

## 7. Production Build & Deployment

To compile the wiper controller for physical deployment on a Raspberry Pi Pico:

```bash
# Compile native C++ firmware sketch
smflow build samples/reference/automotive/wiper-controller/wiper-controller.smflow --target rp2040-pico

# Deploy directly over USB (board in BOOTSEL mode or connected via serial COM port)
smflow deploy samples/reference/automotive/wiper-controller/wiper-controller.smflow --target rp2040-pico
```

The compiler produces a deterministic, self-contained binary running a 10 ms periodic control task with zero external runtime dependencies.
