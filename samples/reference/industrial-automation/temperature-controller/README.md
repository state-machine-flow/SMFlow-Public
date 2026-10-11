# Industrial Temperature Controller Reference Architecture

A production-grade reference implementation of an industrial dual-mode temperature controller designed for deterministic micro-PLCs (**Arduino Opta**) and embedded controllers (**Raspberry Pi Pico**, **SMFlow Simulator**).

This architecture implements closed-loop thermal regulation using analog temperature transmitters (RTD PT100/PT1000, thermocouple transmitter, or precision thermistor), dual-stage deadband hysteresis engines, selectable heating and cooling modes, automated post-heat exhaust cooldown sequences, sensor loop integrity diagnostics, and latched safety alarms with emergency over-temperature purge overrides.

---

## 1. Applications & Engineering Overview

Thermal management systems are ubiquitous across process industries, manufacturing plants, and scientific testing environments:

- **Environmental & Electrical Enclosures**: Outdoor telecommunication enclosures, traffic control cabinets, and battery storage compartments requiring winter freeze protection (heating mode) and summer forced-air ventilation (cooling mode).
- **Laboratory Incubators & Biological Chambers**: Precise culture incubation chambers holding samples at tight thermal bands without wide oscillatory temperature swings or hot spots.
- **Process Heating & Immersion Tanks**: Chemical baths, parts washers, and food pasteurization vessels driven by electric immersion elements requiring positive cooldown ventilation and dry-element burn prevention.
- **Small Industrial Ovens & Curing Chambers**: Adhesive curing, composite baking, and powder coat preheat chambers requiring structured startup sensor stabilization delays and exhaust purging.
- **Environmental Test Fixtures & Burn-In Stations**: Automated qualification fixtures cycling hardware between extreme temperatures with fail-safe thermal runaway interlocks.

### Critical Engineering Challenges Solved

1. **Deadband Hysteresis & Relay Cycling Fatigue**: Simple single-threshold thermostats oscillate rapidly around their setpoint ("chatter"), causing electromagnetic contactor arcing, relay contact welding, and rapid solid-state relay (SSR) thermal fatigue. This flow implements independent cut-in and cut-out hysteresis setpoints with set-reset latches, enforcing deterministic $2.0^\circ\text{C}$ deadbands for heating and $5.0^\circ\text{C}$ deadbands for cooling.
2. **Post-Heating Element Thermal Inertia & Burnout**: High-wattage ceramic, nichrome, and sheath immersion heating elements continue radiating heat into ductwork and housings after electrical power is cut. Abruptly stopping ventilation air traps extreme heat, warping heating coils, tripping bimetallic thermal fuses, and degrading cabinet wiring. The controller enforces an automated **5.0-second cooldown exhaust fan sequence** whenever the heating stage turns off.
3. **Sensor Open/Short Fail-Safe Detection**: Thermocouples commonly fail open (lead wire fatigue or screw terminal loosening), while thermistors or RTD leads often short to conduit ground. An unmonitored broken sensor reads artificial freezing temperatures, causing naive controllers to drive heaters to maximum continuous power, resulting in catastrophic thermal runaway. This flow monitors lower ($-10.0^\circ\text{C}$) and upper ($150.0^\circ\text{C}$) plausibility boundaries, instantly cutting off heat and latching an alarm if sensor wiring fails.
4. **Emergency Over-Temperature Purge Override**: If a solid-state relay fails shorted or an exothermic chemical reaction begins, process temperature may surge toward dangerous levels. When the temperature crosses the critical limit ($90.0^\circ\text{C}$), the controller trips an alarm, locks out the heater contactor, and forces the cooling exhaust fan to run continuously as an active purge.
5. **Startup Sensor Stabilization Delay**: Sensor amplifiers, cold-junction compensators, and analog power rails experience transient settling voltages when main power is applied. A dedicated **3.0-second startup on-delay (TON)** prevents false triggering and output short-cycling during power-up.

---

## 2. System Architecture & Signal Flow

```
+-----------------------------------------------------------------------------------------+
|                  SMFlow Industrial Temperature Controller (Arduino Opta)                |
|                                                                                         |
|   [ Analog Temp Transmitter ] -------> Terminal I1 (AI) ---> [ Plausibility & Limits ]  |
|                                                                      │                  |
|   [ Master Enable Switch ] ----------> Terminal I2 (DI) -+           ├─ Over-Temp Trip  |
|   [ Heating/Cooling Mode ] ----------> Terminal I3 (DI) -+           ├─ Sensor Fault    |
|   [ Alarm Reset Pushbutton ] --------> Terminal I4 (DI) -+           │                  |
|                                                                      ▼                  |
|                                                             [ Master Alarm Latch ]      |
|                                                                      │                  |
|                                                                      ▼                  |
|                                                             [ Safety Permissive ]       |
|                                                                      │                  |
|   [ 3.0s Startup On-Delay ] ─────────────────────────────────────────┼─ Armed Status    |
|                                                                      │                  |
|   [ Heating Hysteresis (58°C–60°C) ] ────────────────────────────────┼─ Heater Command  |
|   [ Cooling Hysteresis (65°C–60°C) ] ────────────────────────────────┼─ Cooler Command  |
|   [ 5.0s Post-Heat Cooldown TOF ] ───────────────────────────────────┴─ Cooldown Active |
|                                                                                         |
|   [ Heater Contactor / SSR ] <──────── RELAY 1 (DO) <─────── [ Interlocked Heater ]     |
|   [ Cooling Fan / Chiller ] <───────── RELAY 2 (DO) <─────── [ Fan / Cooldown / Purge ] |
|   [ Alarm Strobe / Annunciator ] <──── RELAY 3 (DO) <─────── [ Alarm Output ]           |
|   [ Armed / Running Indicator ] <───── RELAY 4 (DO) <─────── [ Active Status ]          |
+-----------------------------------------------------------------------------------------+
```

### Staged Output Architecture

- **Heater Contactor Output (`HeaterOutput`)**:
  - Bound to **RELAY1** on Arduino Opta / **GP20** on RP2040 Pico.
  - Controls electric heating element contactor or solid-state relay (SSR).
  - Strictly interlocked against simultaneous cooling and gated by the Safety Permissive.
- **Cooling Fan Output (`CoolerOutput`)**:
  - Bound to **RELAY2** on Arduino Opta / **GP21** on RP2040 Pico.
  - Controls exhaust fan, circulation blower, or refrigeration solenoid valve.
  - Energized during normal cooling demand, 5.0-second post-heating cooldown sequences, or emergency over-temperature purges.
- **Alarm Annunciator Output (`AlarmOutput`)**:
  - Bound to **RELAY3** on Arduino Opta / **GP22** on RP2040 Pico.
  - Drives high-intensity warning strobe, buzzer, or building management system (BMS) supervisory input.
- **Active / Armed Status Output (`ActiveOutput`)**:
  - Bound to **RELAY4** on Arduino Opta / **GP27** on RP2040 Pico.
  - Illuminates a panel run indicator lamp when the controller is enabled and past its startup stabilization window.

---

## 3. Calibrated Setpoints & Operational Parameters

| Variable Name | Default Value | Engineering Unit | Function & Description |
| :--- | :---: | :---: | :--- |
| `HeatOnTemp` | **58.0** | °C | Heating cut-in threshold. Heater turns ON when temperature falls below this value. |
| `HeatOffTemp` | **60.0** | °C | Heating cut-out threshold. Heater turns OFF when temperature reaches target ($2.0^\circ\text{C}$ deadband). |
| `CoolOnTemp` | **65.0** | °C | Cooling cut-in threshold. Cooler fan turns ON when temperature exceeds this value. |
| `CoolOffTemp` | **60.0** | °C | Cooling cut-out threshold. Cooler fan turns OFF when temperature drops to target ($5.0^\circ\text{C}$ deadband). |
| `OverTempLimit` | **90.0** | °C | Critical high-temperature safety threshold. Trips alarm, cuts heater, and forces cooler fan on. |
| `SensorMin` | **-10.0** | °C | Transducer plausibility lower floor. Readings below indicate sensor short circuit or grounded leads. |
| `SensorMax` | **150.0** | °C | Transducer plausibility upper ceiling. Readings above indicate open thermocouple or broken leads. |
| `timer_startup` | **3000** | Milliseconds | Startup on-delay timer (TON). Enforces a 3.0-second stabilization delay before arming outputs. |
| `timer_cooldown`| **5000** | Milliseconds | Post-heating off-delay timer (TOF). Runs exhaust fan for 5.0 seconds after heater turns off. |

---

## 4. Operating Modes & Control Logic

### 1. Disabled Mode (`EnableSwitch == false`)
- All outputs (`HeaterOutput`, `CoolerOutput`, `ActiveOutput`) are held in the safe de-energized state.
- Sensor plausibility checks continue running in the background.

### 2. Startup Stabilization Phase (`EnableSwitch == true`, $t < 3.0\text{s}$)
- `timer_startup` (TON) timing window is active.
- Outputs remain de-energized while sensor power supplies and analog input filtering stabilize.
- Once 3.0 seconds elapse, `ActiveOutput` illuminates and closed-loop thermal regulation engages.

### 3. Heating Mode (`CoolingMode == false`)
- Intended for environmental enclosures, winter heating, ovens, and process warmers.
- **Cut-In ($T \le 58.0^\circ\text{C}$)**: Process temperature falling to or below `HeatOnTemp` sets the heating demand latch. `HeaterOutput` energizes.
- **Deadband Hold ($58.0^\circ\text{C} < T < 60.0^\circ\text{C}$)**: Hysteresis latch holds heater energized without contactor chatter.
- **Cut-Out ($T \ge 60.0^\circ\text{C}$)**: Reaching target setpoint resets heating demand. `HeaterOutput` immediately de-energizes.
- **Post-Heat Cooldown Sequence**: Upon heater de-energization, `timer_cooldown` (TOF) engages `CoolerOutput` for **5.0 seconds** to flush residual heat from the heating chamber, preventing element degradation.

### 4. Cooling Mode (`CoolingMode == true`)
- Intended for electrical cabinets, summer cooling, refrigeration, and cooling towers.
- **Cut-In ($T \ge 65.0^\circ\text{C}$)**: Process temperature rising to or above `CoolOnTemp` sets the cooling demand latch. `CoolerOutput` energizes.
- **Deadband Hold ($60.0^\circ\text{C} < T < 65.0^\circ\text{C}$)**: Hysteresis latch holds cooling fan energized.
- **Cut-Out ($T \le 60.0^\circ\text{C}$)**: Temperature dropping to target resets cooling demand. `CoolerOutput` de-energizes.

### 5. Emergency Over-Temperature Override & Alarm
- If process temperature reaches or exceeds `OverTempLimit` ($90.0^\circ\text{C}$):
  1. `HeaterOutput` is immediately de-energized via safety permissive gating.
  2. `AlarmOutput` latches ON.
  3. `CoolerOutput` is forced ON unconditionally to provide emergency heat purge ventilation.
- **Set-Dominant Latching**: The alarm cannot be cleared by the operator while the over-temperature condition physically persists. Once the temperature drops below $90.0^\circ\text{C}$, pressing `AlarmReset` clears the alarm and restores normal regulation.

### 6. Sensor Failure Diagnostics
- **Broken Wire / Open Circuit ($T > 150.0^\circ\text{C}$)**: Detects detached thermocouple wire, open RTD element, or disconnected transmitter. Trips master alarm and cuts heater power instantly.
- **Short Circuit / Ground Fault ($T < -10.0^\circ\text{C}$)**: Detects shorted transducer cable or conduit water ingress. Trips master alarm and inhibits heater start.

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
                       |   |   |   |
  0–10V / RTD Temp Tx ─┘   |   |   |
  Master Enable Switch ────┘   |   |
  Cooling Mode Switch ─────────┘   |
  Alarm Reset Pushbutton ──────────┘

                    +------------------------------+
                    |   R1    R2       R3     R4   |
                    +---+-----+--------+------+----+
                        |     |        |      |
  Heater SSR / Contactor ─┘     |        |      |
  Cooling Exhaust Fan ────────┘        |      |
  Alarm Strobe / Horn ─────────────────┘      |
  System Active Lamp ─────────────────────────┘
```

### Raspberry Pi Pico Wiring

```
                                  RASPBERRY PI PICO
                               +---------------------+
  Process Temperature (0–3.3V) | GP26 (ADC0)    GP20 | Heater Contactor Output
  Master Enable Switch         | GP14           GP21 | Cooler Fan Output
  Cooling Mode Switch          | GP15           GP22 | Alarm Annunciator Output
  Alarm Reset Pushbutton       | GP16           GP27 | System Active Output
                               | GND             GND | Power Common (0V)
                               +---------------------+
```

### Signal Connection Summary

| Logical Signal Name | Type | Direction | Arduino Opta Terminal | Raspberry Pi Pico Pin | Electrical Specification |
| :--- | :---: | :---: | :--- | :--- | :--- |
| `ProcessTemperature` | Analog | Input | **I1** | **GP26 (ADC0)** | 0–10V (Opta) / 0–3.3V (Pico) scaled to °C |
| `EnableSwitch` | Digital | Input | **I2** | **GP14** | +24VDC (Opta) / +3.3V (Pico) maintained switch |
| `CoolingMode` | Digital | Input | **I3** | **GP15** | +24VDC (Opta) / +3.3V (Pico) maintained switch |
| `AlarmReset` | Digital | Input | **I4** | **GP16** | +24VDC (Opta) / +3.3V (Pico) NO pushbutton |
| `HeaterOutput` | Digital | Output | **RELAY 1** | **GP20** | SPST 10A dry contact / 3.3V logic to SSR driver |
| `CoolerOutput` | Digital | Output | **RELAY 2** | **GP21** | SPST 10A dry contact / 3.3V logic to fan relay |
| `AlarmOutput` | Digital | Output | **RELAY 3** | **GP22** | SPST 10A dry contact / 3.3V logic to strobe |
| `ActiveOutput` | Digital | Output | **RELAY 4** | **GP27** | SPST 10A dry contact / 3.3V logic to pilot lamp |

---

## 6. Simulation & Verification

The controller comes with an automated test suite ([temperature-controller.smtest](file:///F:/repos/ctacke/SMFlow-Public/samples/reference/industrial-automation/temperature-controller/temperature-controller.smtest)) validating all 18 functional state transitions:

```powershell
# 1. Validate graph topology and I/O bindings
smflow validate samples/reference/industrial-automation/temperature-controller/temperature-controller.smflow --target opta
smflow validate samples/reference/industrial-automation/temperature-controller/temperature-controller.smflow --target rp2040-pico
smflow validate samples/reference/industrial-automation/temperature-controller/temperature-controller.smflow --target simulator

# 2. Execute automated test suite
smflow test samples/reference/industrial-automation/temperature-controller/temperature-controller.smtest

# 3. Simulate interactive execution
smflow simulate samples/reference/industrial-automation/temperature-controller/temperature-controller.smflow
```

### Test Coverage Highlights

- **Startup Delay Inhibit**: Confirms all outputs are held off during the 3.0s power-up stabilization window.
- **Heating Hysteresis**: Verifies cut-in below $58.0^\circ\text{C}$, latching hold at $59.0^\circ\text{C}$, and cut-out at $60.5^\circ\text{C}$.
- **Post-Heat Cooldown Fan**: Verifies the exhaust fan operates for exactly 5.0 seconds after the heater stops.
- **Cooling Hysteresis**: Verifies cut-in above $65.0^\circ\text{C}$, latching hold at $62.0^\circ\text{C}$, and cut-out at $59.5^\circ\text{C}$.
- **Emergency Over-Temperature**: Verifies instant heater cutoff, alarm trip, and forced cooler fan purge at $92.0^\circ\text{C}$.
- **Diagnostic Plausibility**: Verifies sensor short ($-15.0^\circ\text{C}$) and sensor open ($160.0^\circ\text{C}$) faults immediately trip alarms and lock out thermal outputs.
- **Set-Dominant Alarm Behavior**: Verifies that pressing the reset button while a fault condition persists will not clear the alarm.
