# Pneumatic Cylinder Sequencer Reference Architecture

A production-grade reference implementation of an industrial pneumatic actuator sequencer for deterministic micro-PLCs (**Arduino Opta**) and embedded targets (**Raspberry Pi Pico**, **SMFlow Simulator**).

This architecture controls a double-acting pneumatic cylinder through an **Extend → Dwell → Retract** motion sequence using 5/2-way directional solenoid valves and magnetic reed/proximity end-position sensors, with dual watchdog jam timeouts, simultaneous-sensor conflict detection, immediate cycle abort, and set-dominant latched alarms.

---

## 1. Applications & Problem Context

Pneumatic cylinders are the backbone of factory automation, part-handling, and packaging machinery:

- **Assembly Fixtures & Part Clamps**: Clamping workpieces firmly during automated drilling, welding, or inspection; dwelling under full pneumatic pressure for a precise duration before releasing.
- **Small Assembly Machines & Presses**: Driving crimping, stamping, pressing, or riveting heads with confirmed full stroke before allowing subsequent machine steps.
- **Part Ejectors & Sorting Diverters**: Rapidly extending into a conveyor pocket to eject finished or rejected components into bins, then returning to home position.
- **Transfer Slides & Pick-and-Place Stations**: Advancing end-of-arm tooling between pick and drop coordinates.

### Critical Operational Challenges Solved

1. **Undetected Mechanical Jams**: If a cylinder encounters an obstruction (e.g. misaligned raw material or mechanical interference), standard open-loop timer systems leave solenoids energized indefinitely, leading to overheated solenoid coils, bent piston rods, and damaged tooling. The controller incorporates **individual travel watchdog timers** (`2.5s`) for both extend and retract strokes.
2. **Sensor Failure & Short-Circuit Failures**: In dirty manufacturing environments, magnetic reed switches or inductive proximity sensors suffer cable wear, vibration misalignment, or metal particle contamination. If both retracted and extended sensors trigger simultaneously, naive logic can stall or violently chatter; the controller implements immediate **Simultaneous Sensor Conflict Detection**.
3. **Premature Cycle Triggering**: Initiating an extend stroke when the cylinder is not verified at the home position can crush tooling or crash adjacent mechanisms. The controller strictly enforces a **Home Confirmation Permissive** before honoring start commands.
4. **Immediate Emergency & Cycle Abort**: The `StopButton` provides clean, instant cancellation across all phases (Extend, Dwell, and Retract), de-energizing directional solenoids immediately without leaving dangling state.

---

## 2. System Architecture & Signal Flow

```
+-----------------------------------------------------------------------------------------+
|                  SMFlow Pneumatic Cylinder Sequencer (Arduino Opta)                     |
|                                                                                         |
|   [ Start Pushbutton (NO) ] --------> Terminal I1 (DI) ---+                             |
|   [ Stop Pushbutton (NC/NO) ] ------> Terminal I2 (DI) ---+-> [ Cycle & Stage Logic ]   |
|   [ Reset Pushbutton (NO) ] --------> Terminal I3 (DI) ---+           │                 |
|                                                                       ▼                 |
|   [ Retracted Reed Switch ] --------> Terminal I4 (DI) ---> [ Position Confirmation ]   |
|   [ Extended Reed Switch ] ---------> Terminal I5 (DI) ---> [ & Conflict Detection ]   |
|                                                                       │                 |
|                                                                       ▼                 |
|                                                             [ Watchdog Timers ]         |
|                                                             (Extend 2.5s / Retract 2.5s)|
|                                                                       │                 |
|                                                                       ▼                 |
|   [ Extend Solenoid Valve ] <------- RELAY 1 (DO) <-------- [ Directional Interlock ]   |
|   [ Retract Solenoid Valve ] <------ RELAY 2 (DO) <-------- [ & Safety Permissive ]     |
|   [ In-Cycle Indicator Lamp ] <----- RELAY 3 (DO) <-------- [ In-Cycle Status ]         |
|   [ Alarm Strobe / Horn ] <--------- RELAY 4 (DO) <-------- [ Jam & Sensor Fault Latch] |
+-----------------------------------------------------------------------------------------+
```

### Actuator & Output Interface

- **Extend Solenoid (`ExtendSolenoid`)**:
  - Bound to **RELAY1** on Arduino Opta / **GP20** on RP2040 Pico.
  - Pilots the advance pilot port of a 5/2-way double solenoid valve (or single spring-return solenoid).
  - Energized during Stage 1 (Extend) and maintained during Stage 2 (Dwell) to maintain clamping force.
- **Retract Solenoid (`RetractSolenoid`)**:
  - Bound to **RELAY2** on Arduino Opta / **GP21** on RP2040 Pico.
  - Pilots the return pilot port of the 5/2-way valve.
  - Energized during Stage 3 (Retract) until the home sensor is confirmed.
  - **Directional Interlock**: Software mutually excludes Extend and Retract outputs, preventing coil cross-conduction.
- **In-Cycle Output (`InCycleOutput`)**:
  - Bound to **RELAY3** on Arduino Opta / **GP22** on RP2040 Pico.
  - Illuminates a blue/white operator panel lamp indicating cycle execution.
- **Alarm Output (`AlarmOutput`)**:
  - Bound to **RELAY4** on Arduino Opta / **GP27** on RP2040 Pico.
  - Drives an audible buzzer or red strobe annunciator upon any latched fault.

---

## 3. Sequence Timing & Parameter Specifications

| Parameter / Timer | Preset Value | Function & Description |
| :--- | :---: | :--- |
| `timer_dwell` | **1500 ms (1.5s)** | Dwell timer maintaining full extend position for clamping or part processing. |
| `timer_extend_timeout` | **2500 ms (2.5s)** | Watchdog timer detecting piston stall or obstruction while advancing to work position. |
| `timer_retract_timeout` | **2500 ms (2.5s)** | Watchdog timer detecting piston stall or guide binding while returning home. |

---

## 4. Operating Phases & Safety Logic

```
   [Home Position] ──► Start ──► [Extend Phase] ──► ExtendedSensor ──► [Dwell Phase]
         ▲                                                                   │
         │                                                            1.5s Dwell Done
         │                                                                   │
         └──────── RetractedSensor ◄── [Retract Phase] ◄─────────────────────┘
```

### 1. Idle / Ready State
- Cylinder confirmed at home: `RetractedSensor == true`, `ExtendedSensor == false`.
- All solenoid outputs de-energized.
- Machine is armed and waiting for `StartButton`.

### 2. Stage 1: Extend Phase
- Triggered by `StartButton` when verified at Home and un-faulted.
- `ExtendSolenoid` energizes; `InCycleOutput` illuminates.
- Piston moves forward, releasing `RetractedSensor`.
- `timer_extend_timeout` (2.5s) begins timing.
- **Normal Completion**: Piston triggers `ExtendedSensor`, resetting the Extend latch and stopping the watchdog.
- **Jam Trip**: If 2.5s elapses without reaching `ExtendedSensor`, the watchdog trips, immediately killing valve power and latching the alarm.

### 3. Stage 2: Dwell Phase
- Cylinder holds at work position (`ExtendedSensor == true`).
- `ExtendSolenoid` remains energized to maintain full pneumatic clamping force.
- `timer_dwell` (1.5s) counts down.
- **Completion**: At 1.5s, the dwell timer triggers Stage 3.

### 4. Stage 3: Retract Phase
- `ExtendSolenoid` de-energizes; `RetractSolenoid` energizes.
- Piston travels backward, releasing `ExtendedSensor`.
- `timer_retract_timeout` (2.5s) begins timing.
- **Normal Completion**: Piston hits `RetractedSensor` (Home). The Retract latch resets, de-energizing `RetractSolenoid` and extinguishing `InCycleOutput`. Sequence returns to Idle.
- **Jam Trip**: If 2.5s elapses without confirming Home, the retract watchdog trips, killing valve power and latching the alarm.

### 5. Jam & Sensor-Failure Diagnostics
- **Simultaneous Sensor Conflict**: If `RetractedSensor AND ExtendedSensor` are true simultaneously (shorted wire or switch contact failure), the system trips instantly without moving.
- **Set-Dominant Alarm Latching**: When any jam or sensor fault trips, `AlarmOutput` latches ON. The operator cannot clear the alarm by pressing `ResetButton` while a sensor short remains active.
- **Cycle Abort**: Pressing `StopButton` immediately clears all motion stages and turns off all solenoids.

---

## 5. Hardware Wiring & Pin Mapping

### Arduino Opta Micro-PLC Wiring Diagram

```
                       ARDUINO OPTA PRO MICRO-PLC
                    +------------------------------+
                    |  +24VDC                0VDC  |
                    |  (PWR+)               (PWR-) |
                    +------------------------------+
                    |  I1   I2   I3   I4   I5      |
                    +--+----+----+----+----+-------+
                       |    |    |    |    |
  Cycle Start Pushbutton ───┘    |    |    |
  Cycle Stop Pushbutton ─────────┘    |    |
  Alarm Reset Pushbutton ─────────────┘    |
  Retracted Reed Switch (Home) ────────────┘
  Extended Reed Switch (Work) ─────────────┘

                    +------------------------------+
                    |   R1       R2       R3    R4 |
                    | [RELAY1] [RELAY2] [RELAY3] [RELAY4] |
                    +----+--------+-------+-----+--+
                         |        |       |     |
  Extend Solenoid Valve ─┘        |       |     |
  Retract Solenoid Valve ─────────┘       |     |
  In-Cycle Indicator Lamp ────────────────┘     |
  Alarm Strobe / Horn ──────────────────────────┘
```

### Pin Binding Reference (`pneumatic-cylinder-sequencer.iomap`)

| Logical Signal | Signal Type | Arduino Opta | Raspberry Pi Pico | Simulator | Description |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `StartButton` | Digital Input | `I1` | `GP14` | `virtual.StartButton` | Momentary cycle start pushbutton |
| `StopButton` | Digital Input | `I2` | `GP15` | `virtual.StopButton` | Cycle stop / abort pushbutton |
| `ResetButton` | Digital Input | `I3` | `GP16` | `virtual.ResetButton` | Alarm reset pushbutton |
| `RetractedSensor`| Digital Input | `I4` | `GP17` | `virtual.RetractedSensor`| Retracted reed switch (Home) |
| `ExtendedSensor` | Digital Input | `I5` | `GP18` | `virtual.ExtendedSensor` | Extended reed switch (Work) |
| `ExtendSolenoid` | Digital Output| `RELAY1` | `GP20` | `virtual.ExtendSolenoid` | 5/2 valve extend coil |
| `RetractSolenoid`| Digital Output| `RELAY2` | `GP21` | `virtual.RetractSolenoid`| 5/2 valve retract coil |
| `InCycleOutput` | Digital Output| `RELAY3` | `GP22` | `virtual.InCycleOutput` | Cycle in progress lamp |
| `AlarmOutput` | Digital Output| `RELAY4` | `GP27` | `virtual.AlarmOutput` | Jam / fault alarm indicator |

---

## 6. Verification & CLI Usage

### Validate Visual Graph
```bash
# Validate core flow
smflow validate samples/reference/industrial-automation/pneumatic-cylinder-sequencer/pneumatic-cylinder-sequencer.smflow

# Validate for Arduino Opta
smflow validate samples/reference/industrial-automation/pneumatic-cylinder-sequencer/pneumatic-cylinder-sequencer.smflow --target opta
```

### Run Automated Graph Test Suite
Execute the 17 automated tests verifying normal sequence, dwell holding, jam timeouts, sensor conflict, and stop cancellation:
```bash
smflow test samples/reference/industrial-automation/pneumatic-cylinder-sequencer/pneumatic-cylinder-sequencer.smflow samples/reference/industrial-automation/pneumatic-cylinder-sequencer/pneumatic-cylinder-sequencer.smtest
```

### Build Ahead-of-Time C++ Firmware
```bash
# Generate C++ sketch for Arduino Opta
smflow build samples/reference/industrial-automation/pneumatic-cylinder-sequencer/pneumatic-cylinder-sequencer.smflow --target opta --out ./build/opta

# Compile native Linux binary
smflow build samples/reference/industrial-automation/pneumatic-cylinder-sequencer/pneumatic-cylinder-sequencer.smflow --target linux-x64 --out ./build/linux
```
