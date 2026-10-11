# Industrial Pump Controller Reference Architecture

A production-grade reference implementation of an industrial pump controller designed for deterministic micro-PLCs (**Arduino Opta**) and embedded controllers (**Raspberry Pi Pico**, **SMFlow Simulator**).

This architecture implements closed-loop process regulation using analog pressure, level, or flow transmitters with calibrated hysteresis, anti-short-cycling minimum run and rest timers, dry-run and motor thermal overload interlocks, a 3-position Hand-Off-Auto (HOA) operating mode selector, and latched safety alarms with manual operator reset.

---

## 1. Applications & Engineering Overview

Industrial fluid handling systems span critical municipal, agricultural, and industrial infrastructure:

- **Deep Well Submersible Pumps**: Groundwater extraction into pressure tanks or cisterns, requiring strict anti-rapid-recycle protection to avoid heat accumulation in water-cooled submersible motor windings and dry-run protection when the water table recedes below pump intake.
- **Sump & Dewatering Systems**: Stormwater and wastewater pit evacuation, requiring dual-threshold hysteresis to avoid contactor chatter around turbulent fluid levels and dry-run cutoff when suction loses prime.
- **Agricultural Irrigation & Center Pivots**: Constant-pressure booster sets supplying drip lines or pivot spans, requiring minimum run timers to prevent water hammer surges and check valve slam.
- **Industrial Fluid Transfer & Tank Level Control**: Batch transfer between chemical, process, or CIP (Clean-in-Place) storage vessels with fail-safe transducer loop diagnostic monitoring.

### Critical Challenges Solved

1. **Short-Cycling & Contactor Chattering**: Fluid surface turbulence, pressure transients, and water hammer waves cause unbuffered threshold switches to chatter at high frequencies. Every start event draws locked-rotor inrush current (typically 6× to 8× full load current / FLC), causing contactor pitting, starter coil burnout, and motor overheating.
2. **Dry-Run Impeller Destruction**: Centrifugal and positive displacement pumps depend on the pumped fluid for bearing lubrication and mechanical face seal cooling. Running dry for as little as 30 to 60 seconds generates extreme friction, distorting elastomeric impellers, cracking ceramic/carbon seals, and warping diffusers.
3. **Motor Thermal Overload**: High-head deadheading, blocked impellers, bearing seizure, or low supply voltage cause motor winding temperatures to surge. Thermal overload inputs must disconnect the motor contactor instantly, latch the fault state, and prohibit restart until the motor has cooled and an operator acknowledges the condition.
4. **Anti-Rapid-Cycle Rest Delay**: Submersible and TEFC pump motors dissipate rotor heat slowly through stator housings. Attempting to restart immediately after stopping traps thermal energy and strains the power distribution bus. A deterministic minimum rest delay guarantees sufficient cool-down and permits fluid columns to settle before re-energizing.

---

## 2. System Architecture & Signal Flow

```
+-----------------------------------------------------------------------------------------+
|                        SMFlow Industrial Pump Controller (Arduino Opta)                 |
|                                                                                         |
|   [ 4–20mA / 0–10V Sensor ] -------> Terminal I1 (AI) ---> [ Sensor Plausibility ]       |
|                                                                    │                    |
|   [ HOA Switch (AUTO) ] -----------> Terminal I2 (DI) -+           ▼                    |
|   [ HOA Switch (HAND) ] -----------> Terminal I3 (DI) -+-> [ Mode Interlock ]           |
|                                                        │           │                    |
|   [ Manual Run Button ] -----------> Terminal I4 (DI) -+           ▼                    |
|                                                            [ Hysteresis Engine ]        |
|   [ Dry-Run Switch / Probe ] ------> Terminal I5 (DI) -+           │                    |
|   [ Overload Relay Contact ] ------> Terminal I6 (DI) -+-> [ Fault & Alarm Latch ]      |
|   [ Alarm Reset Pushbutton ] ------> Terminal I7 (DI) -+           │                    |
|                                                                    ▼                    |
|                                                            [ Run / Rest Timers ]        |
|                                                                    │                    |
|   [ Pump Starter Relay ] <---------- RELAY 1 (DO) <-------- [ Safety Permissive ]       |
|   [ Alarm Strobe / Horn ] <--------- RELAY 2 (DO) <-------- [ Latched Alarm ]           |
|   [ Run Indicator Lamp ] <---------- RELAY 3 (DO) <-------- [ Contactor Feedback ]      |
|   [ Auto Mode Telemetry ] <--------- RELAY 4 (DO) <-------- [ Mode Verification ]       |
+-----------------------------------------------------------------------------------------+
```

### Staged Output Architecture

- **Pump Contactor Output (`PumpContactor`)**:
  - Bound to **RELAY1** on Arduino Opta / **GP20** on RP2040 Pico.
  - Directly pilots the 24VDC or 120VAC coil of a NEMA / IEC magnetic motor starter with auxiliary contacts.
  - Strictly gated by the Safety Permissive interlock: de-energizes immediately upon any fault.
- **Alarm Output (`AlarmOutput`)**:
  - Bound to **RELAY2** on Arduino Opta / **GP21** on RP2040 Pico.
  - Energizes an audible annunciator horn, rotating strobe, or SCADA alarm input upon any latched fault.
- **Pump Running Status Output (`PumpRunningOutput`)**:
  - Bound to **RELAY3** on Arduino Opta / **GP22** on RP2040 Pico.
  - Drives a green operator panel run lamp and SCADA digital telemetry channel.
- **Auto Mode Status Output (`AutoModeOutput`)**:
  - Bound to **RELAY4** on Arduino Opta / **GP27** on RP2040 Pico.
  - Drives an amber panel indicator confirming closed-loop automatic regulation is active and valid.

---

## 3. Calibrated Setpoints & Operational Parameters

| Variable Name | Default Value | Engineering Unit | Function & Description |
| :--- | :---: | :---: | :--- |
| `StartThreshold` | **35.0** | PSI / % level | Cut-in threshold that initiates pump start demand in automatic mode. |
| `StopThreshold` | **55.0** | PSI / % level | Cut-out threshold that clears pump start demand, providing a **20.0 unit hysteresis deadband**. |
| `SensorMin` | **0.0** | PSI / % level | Transducer loop plausibility floor; readings below indicate broken wire or short-to-ground. |
| `SensorMax` | **100.0** | PSI / % level | Transducer loop plausibility ceiling; readings above indicate open circuit or transmitter failure. |
| `PumpDownMode` | **false** | Boolean | Direction selector: `false` = Pump-Up (Pressure/Well fill), `true` = Pump-Down (Sump/Drainage). |
| `timer_min_run` | **5000** | Milliseconds | Minimum run off-delay timer (5.0s). Enforces runtime to prevent short-cycling. |
| `timer_min_rest` | **5000** | Milliseconds | Minimum rest off-delay timer (5.0s). Enforces anti-rapid-recycle cool-down between cycles. |

---

## 4. Operating Modes & Control Logic

### 1. OFF Mode (`AutoSwitch == false` and `ManualSwitch == false`)
- The 3-position HOA selector is in the center OFF position.
- All pump outputs are de-energized.
- Alarm latching and monitoring remain vigilant in the background.

### 2. AUTO Mode (`AutoSwitch == true`, `ManualSwitch == false`)
- `AutoModeOutput` illuminates to confirm valid automatic operation.
- **Pump-Up Mode (`PumpDownMode == false`)** (Well / Pressure Tank Booster):
  - When `ProcessVariable <= StartThreshold` (35.0 PSI), process demand sets `latch_process_demand`.
  - While pressure rises between 35.0 and 55.0 PSI, the hysteresis latch holds the pump running.
  - When `ProcessVariable >= StopThreshold` (55.0 PSI), demand clears and the pump stops (after minimum run time has elapsed).
- **Pump-Down Mode (`PumpDownMode == true`)** (Sump Pit / Wastewater Dewatering):
  - When `ProcessVariable >= StartThreshold` (high water cut-in), process demand sets.
  - When `ProcessVariable <= StopThreshold` (low water cut-out), process demand resets.
- **HOA Contact Conflict Protection**:
  - If both `AutoSwitch` and `ManualSwitch` are true simultaneously (mechanical switch fault or shorted wiring), the controller immediately invalidates both modes and inhibits pump operation.

### 3. MANUAL / HAND Mode (`ManualSwitch == true`, `AutoSwitch == false`)
- Automatic sensor thresholds are bypassed for commissioning, priming, or emergency drainage.
- The pump runs while `ManualStart` is held active.
- **Safety Interlocks Remain Enforced**: Overload and dry-run faults immediately trip the pump in Manual mode; the operator cannot override electrical or thermal motor protection.

### 4. Minimum Run & Minimum Rest Time Protection
- **Minimum Run Time (Anti-Short-Cycling)**:
  - When the pump starts, `timer_min_run` engages for **5.0 seconds**.
  - If process demand clears early (e.g., pressure wave spike or turbulent float bobbing), the pump continues running until the 5.0s window completes, preventing rapid stop-start fatigue.
  - **Safety Override**: Any active fault (dry-run or overload) overrides minimum run time instantly to protect physical equipment.
- **Minimum Rest Time (Anti-Rapid-Recycle)**:
  - When the pump stops after a cycle, `timer_min_rest` holds for **5.0 seconds**.
  - During this rest window, new start attempts (automatic or manual) are locked out.
  - Once the 5.0s rest delay elapses, the controller smoothly permits restarting.

### 5. Alarm Latching & Fail-Safe Reset
- If `DryRunFault`, `OverloadFault`, or a sensor out-of-range condition trips:
  1. The pump contactor de-energizes instantly.
  2. The alarm latch (`latch_alarm`) sets and illuminates `AlarmOutput`.
  3. The alarm remains latched even if water returns or the overload cools down.
- **Reset Inhibit**: Pressing `AlarmReset` while a fault contact is still physically active will NOT clear the alarm (set-dominant latching). The fault must physically clear before the operator can reset the system.

---

## 5. Hardware Wiring & Pin Mapping

### Arduino Opta Micro-PLC Wiring

```
                       ARDUINO OPTA PRO MICRO-PLC
                    +------------------------------+
                    |  +24VDC                0VDC  |
                    |  (PWR+)               (PWR-) |
                    +------------------------------+
                    |  I1  I2  I3  I4  I5  I6  I7  |
                    +--+---+---+---+---+---+---+---+
                       |   |   |   |   |   |   |
  4–20mA Tx (+24V Loop)┘   |   |   |   |   |   |
  HOA Switch AUTO Contact ─┘   |   |   |   |   |
  HOA Switch HAND Contact ─────┘   |   |   |   |
  Manual Start Pushbutton ─────────┘   |   |   |
  Dry-Run Float Switch (NC/NO) ────────┘   |   |
  Motor Overload Trip Contact ─────────────┘   |
  Alarm Reset Pushbutton ──────────────────────┘

                    +------------------------------+
                    |   R1    R2       R3     R4   |
                    | [RELAY1] [RELAY2] [RELAY3] [RELAY4] |
                    +----+-----+----+----+----+----+
                         |          |         |    |
  Motor Starter Contactor┘          |         |    |
  Alarm Strobe / Horn (120VAC/24V) ─┘         |    |
  Green Run Indicator Lamp ───────────────────┘    |
  Amber Auto Telemetry / Lamp ─────────────────────┘
```

### Pin Binding Reference (`pump-controller.iomap`)

| Logical Signal | Signal Type | Arduino Opta | Raspberry Pi Pico | Simulator | Description |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `ProcessVariable` | Analog Input | `I1` | `GP26` (ADC0) | `virtual.ProcessVariable` | 4–20mA / 0–10V analog input (0–100.0) |
| `AutoSwitch` | Digital Input | `I2` | `GP14` | `virtual.AutoSwitch` | HOA Switch AUTO position |
| `ManualSwitch` | Digital Input | `I3` | `GP15` | `virtual.ManualSwitch` | HOA Switch HAND position |
| `ManualStart` | Digital Input | `I4` | `GP16` | `virtual.ManualStart` | Manual Start pushbutton |
| `DryRunFault` | Digital Input | `I5` | `GP17` | `virtual.DryRunFault` | Low-level / dry-run switch |
| `OverloadFault` | Digital Input | `I6` | `GP18` | `virtual.OverloadFault` | Thermal overload relay trip |
| `AlarmReset` | Digital Input | `I7` | `GP19` | `virtual.AlarmReset` | Operator alarm reset button |
| `PumpContactor` | Digital Output | `RELAY1` | `GP20` | `virtual.PumpContactor` | Primary motor starter contactor |
| `AlarmOutput` | Digital Output | `RELAY2` | `GP21` | `virtual.AlarmOutput` | General alarm horn / strobe |
| `PumpRunningOutput`| Digital Output | `RELAY3` | `GP22` | `virtual.PumpRunningOutput`| Pump running indicator lamp |
| `AutoModeOutput` | Digital Output | `RELAY4` | `GP27` | `virtual.AutoModeOutput` | Auto mode status indicator |

---

## 6. Verification & CLI Usage

### Validate Project Graph and Target Bindings
```bash
# Validate core visual graph
smflow validate samples/reference/industrial-automation/pump-controller/pump-controller.smflow

# Validate targeting Arduino Opta
smflow validate samples/reference/industrial-automation/pump-controller/pump-controller.smflow --target opta

# Validate targeting Raspberry Pi Pico
smflow validate samples/reference/industrial-automation/pump-controller/pump-controller.smflow --target rp2040-pico
```

### Run Automated Graph Test Suite
Execute the 18 automated regression tests covering hysteresis, minimum run/rest timings, and fault latching:
```bash
smflow test samples/reference/industrial-automation/pump-controller/pump-controller.smflow samples/reference/industrial-automation/pump-controller/pump-controller.smtest
```

### Build Ahead-of-Time C++ Firmware
```bash
# Emit native C++ sketch for Arduino Opta
smflow build samples/reference/industrial-automation/pump-controller/pump-controller.smflow --target opta --out ./build/opta

# Compile native Linux binary
smflow build samples/reference/industrial-automation/pump-controller/pump-controller.smflow --target linux-x64 --out ./build/linux
```
