# Automotive Retrofit Climate-Controlled Seat Module (CCSM) — Reference Architecture

This document specifies the technical architecture, electrical interfaces, control algorithms, functional safety requirements, and fail-safe state machines for an SMFlow-based **Climate-Controlled Seat Module (CCSM)** designed as a standalone electronic controller for retrofit heated and ventilated automotive seats.

---

## 1. Problem Statement & Automotive Retrofit Context

Luxury OEM seats (e.g. Lincoln Continental, Cadillac Escalade, Ford F-150 Platinum, Porsche 18-Way Adaptive Sport Seats) and high-end aftermarket systems (e.g. Recaro Sportster CS Climate, Katzkin Degreez, Gentex) feature integrated heating pads and forced-air blower fans.

In modern production vehicles, seat climate control is tightly integrated into the vehicle's multiplexed architecture:
- Commands originate at the central infotainment / HVAC head unit.
- The Body Control Module (BCM) relays setpoints over Local Interconnect Network (LIN) or Controller Area Network (CAN).
- A factory Climate-Controlled Seat Module (CCSM / HSM) underneath the seat translates digital frames into pulse-width modulated (PWM) actuator drives.

When these seats are salvaged or transplanted into:
- Classic truck restomods (e.g., Chevy C10, K5 Blazer, Ford F-100, Bronco)
- Overland expedition trucks and camper conversions
- Vintage muscle cars and pro-touring builds
- Kit cars, custom chassis, or restomod sports cars

**The factory multiplexed LIN/CAN communication is missing.** Hardwiring 12V directly to heating elements or fans results in either no operation or uncontrollable runaway heating that burns leather, damages element wire, and poses severe safety hazards to passengers.

This reference flow provides a complete, deterministic, standalone replacement for the missing vehicle network, restoring full 3-level heating, 3-level ventilation cooling, closed-loop thermostatic setpoint regulation, soft-start element protection, sensor fault detection, and post-ignition rundown timing.

---

## 2. Electrical Interface & Terminal Specifications

The module interfaces with five input channels and five output channels:

```
+-----------------------------------------------------------------------------------------+
|                  Automotive Climate-Controlled Seat Controller (CCSM)                    |
|                                                                                         |
|  [INPUTS]                                                                [OUTPUTS]      |
|  Switched +12V (Ignition)    ──[12V-to-3.3V Opto]──────► GP14                           |
|  Seat Occupied Pressure Pad  ──[GND Pull-to-Low]───────► GP15                           |
|  Cool/Heat Mode Switch       ──[SPST Toggle]───────────► GP13                           |
|  Climate Level Pot / Dial    ──[0–3.3V Divider]────────► GP26 (ADC0)                    |
|  Seat Cushion Thermistor     ──[10k NTC Divider]───────► GP27 (ADC1)                    |
|                                                                                         |
|                                                          GP16 ──► Heater MOSFET (PWM)   |
|                                                          GP17 ──► Blower Fan (PWM)      |
|                                                          GP18 ──► Heat Amber LED (DO)   |
|                                                          GP19 ──► Cool Blue LED (DO)    |
|                                                          GP20 ──► Fault Red MIL (DO)    |
+-----------------------------------------------------------------------------------------+
```

### 2.1 Inputs

1. **`Ignition` (GP14)**:
   - **Signal**: Vehicle Switched Ignition / Accessory (RUN / ACC) bus (+12V nominal).
   - **Interface**: Level-shifted via optocoupler or resistor divider (10 k$\Omega$ / 3.3 k$\Omega$) with TVS diode clamp (e.g. SMAJ15A) to protect against automotive load-dump transients (ISO 7637-2).
   - **Function**: Initiates operating state and provides master reset signal for safety fault latches when key is cycled OFF.

2. **`SeatOccupied` (GP15)**:
   - **Signal**: Seat bottom cushion pressure-sensitive membrane switch (normally open).
   - **Interface**: Connected between GP15 and GND with an internal or external 10 k$\Omega$ pull-up resistor to 3.3V. When an occupant sits, resistance drops below 1 k$\Omega$, pulling GP15 LOW (inverted to active-high logical `SeatOccupied = true`).
   - **Function**: Prevents power waste, localized heat buildup, and fire hazards on unoccupied seats.

3. **`CoolMode` (GP13)**:
   - **Signal**: Single-pole single-throw (SPST) toggle or rocker switch.
   - **Interface**: Ground-referenced digital input with pull-up.
   - **Logic**: `false` = Heating Mode, `true` = Ventilation / Cooling Mode.

4. **`LevelSetting` (GP26 / ADC0)**:
   - **Signal**: Cockpit rotary potentiometer (10 k$\Omega$) or 4-position resistor-divider step switch (OFF, 1, 2, 3).
   - **Voltage Range**: 0.0V to 3.3V.
   - **Threshold Decoding**:
     - `LevelSetting < 0.5` $\implies$ **OFF (Level 0)**
     - `0.5 <= LevelSetting < 1.5` $\implies$ **Low (Level 1)**
     - `1.5 <= LevelSetting < 2.5` $\implies$ **Medium (Level 2)**
     - `LevelSetting >= 2.5` $\implies$ **High (Level 3)**

5. **`SeatTemp` (GP27 / ADC1)**:
   - **Signal**: Negative Temperature Coefficient (NTC) thermistor embedded directly beneath seat cushion upholstery.
   - **Scaling**: Calibrated in °C. Nominal automotive operating window spans -10.0°C to +85.0°C.

### 2.2 Outputs

1. **`HeaterPwm` (GP16)**:
   - **Signal**: High-current PWM gate drive.
   - **Actuator**: High-side automotive smart switch (e.g. Infineon PROFET BTS7008-1EPP or discrete P-channel MOSFET like IRF4905) switching +12V battery power to cushion and backrest heating pads.
   - **Frequency**: 10 Hz to 100 Hz low-frequency PWM (avoids electromagnetic interference with audio / radio systems while ensuring smooth thermal output).

2. **`FanPwm` (GP17)**:
   - **Signal**: 25 kHz open-drain / logic-level PWM speed command driving brushless seat blower fans (e.g. Delta BFB1012, Sunon MagLev blowers used in OEM climate seats).
   - **Range**: 0.00 (fan off) to 1.00 (maximum airflow).

3. **`HeatIndicator` (GP18)**:
   - **Signal**: Logic output driving cockpit Amber/Red LED through 2N7002 N-FET.

4. **`CoolIndicator` (GP19)**:
   - **Signal**: Logic output driving cockpit Blue LED through 2N7002 N-FET.

5. **`FaultIndicator` (GP20)**:
   - **Signal**: Diagnostic Malfunction Indicator Lamp (MIL) / Red warning LED indicating latched over-temperature or thermistor circuit faults.

---

## 3. Regulation Algorithms & Physical Considerations

### 3.1 Closed-Loop Thermostatic Setpoint Regulation
In heating mode, the controller implements thermostatic setpoint regulation to maintain occupant comfort without overheating:

$$\text{Heater Gate} = \begin{cases} 
\text{Active (with Soft-Start)} & \text{if } T_{\text{seat}} < T_{\text{target}} \\ 
0.00 & \text{if } T_{\text{seat}} \ge T_{\text{target}} 
\end{cases}$$

- **Level 1 (Low)**: $T_{\text{target}} = 32.0^\circ\text{C}$ (gentle warming for cool mornings).
- **Level 2 (Medium)**: $T_{\text{target}} = 37.0^\circ\text{C}$ (matched to human core body temperature for extended highway comfort).
- **Level 3 (High)**: $T_{\text{target}} = 42.0^\circ\text{C}$ (rapid winter warm-up).

### 3.2 Heater Soft-Start Dynamics
A cold carbon-fiber heating mat or nichrome grid has a low electrical resistance at sub-freezing temperatures ($R \approx 1.0\,\Omega$ to $1.5\,\Omega$). Instantaneous 100% duty cycle application draws an inrush spike exceeding 12 A:
1. Voltage transients sag the vehicle's 12V auxiliary rail.
2. Rapid thermal expansion induces mechanical stress at the crimp terminals between copper lead wires and carbon-fiber heating weave.

The controller introduces a **3.0-second soft-start timer (`timer_soft_start`)**:
- During the first 3.0s of heating activation, duty cycle is clamped to **25% (`DutySoftStart = 0.25`)**.
- After 3.0s of continuous activation, the duty cycle seamlessly transitions to the full level command (**35%**, **65%**, or **95%**).
- If heating is interrupted (e.g., setpoint achieved, seat vacated, or mode changed), the soft-start timer instantly resets.

```text
Heating Demand  ───┐
                   │
                   ▼
       [TON Timer: 3.0 seconds]
             │          │
    (t < 3s) │          │ (t >= 3s)
             ▼          ▼
       Clamp at 25%   Full Duty (35% / 65% / 95%)
```

---

## 4. Functional Safety & Fault Management

The controller adheres to automotive thermal protection principles (SAE J2234 / ISO 13732-1) to protect passengers against skin burns and vehicle interiors against thermal runaway:

### 4.1 Safety Thresholds

1. **Over-Temperature Cutoff ($T_{\text{seat}} > 45.0^\circ\text{C}$)**:
   - Medical consensus establishes that continuous skin contact with surfaces above 44°C–45°C can cause epidermal burns over extended durations.
   - If `SeatTemp > 45.0°C`, the controller immediately asserts `gate_fault_trip`.

2. **Sensor Short-Circuit Detection ($T_{\text{seat}} < 0.0^\circ\text{C}$)**:
   - In standard thermistor divider networks, a short between the signal wire and seat chassis ground pulls the ADC input to 0V (or extreme negative temperature).
   - If `SeatTemp < 0.0°C`, the controller detects this as an electrical wiring short.

3. **Sensor Open-Circuit Detection ($T_{\text{seat}} > 80.0^\circ\text{C}$)**:
   - A broken lead, dislodged pin, or disconnected harness pulls the divider toward the reference rail, producing an abnormally high reading.
   - If `SeatTemp > 80.0°C`, the controller detects this as an open circuit.

### 4.2 Latched Fail-Safe Operation
- When any fault condition occurs, a `set-reset` latch (`latch_fault`) sets `Q = true`.
- Both `HeaterPwm` and `FanPwm` are immediately forced to `0.00`.
- `FaultIndicator` is turned ON.
- **Latching Guarantee**: The fault status remains locked even if the sensor reading returns to normal (e.g., an intermittent wire bouncing back).
- **Clearing Mechanism**: The latch can only be cleared by cycling the vehicle ignition key OFF (`not_ign` connected to `latch_fault.R`), forcing the driver to acknowledge the event.

---

## 5. Retained Accessory Power & Ignition-Off Rundown

High-output seat heating elements draw significant power ($\approx 60\text{ W}$ to $120\text{ W}$ per seat). Leaving heaters energized when an engine is stopped rapidly discharges the vehicle starting battery.

The controller implements an **off-delay timer (`timer_ign_timeout`, TOF with 10.0s preset)**:
- While `Ignition == true`, `timer_ign_timeout.Q` remains `true`.
- When `Ignition` transitions to `false` (e.g. driver turns key to accessory or shuts off engine):
  - `timer_ign_timeout.Q` remains `true` for exactly **10.0 seconds**.
  - During this rundown interval, heating and ventilation remain operational if the occupant remains seated.
  - When the 10.0s preset expires, `gate_power_enable` goes `false`, de-energizing all actuators and indicator lights.
- This prevents accidental battery discharge while supporting smooth transitions during vehicle stalling or stop-start cycling.

---

## 6. Full Operational State Matrix

| State | Ignition | Occupied | Mode | Level | Sensed Temp | Heater PWM | Fan PWM | Heat LED | Cool LED | Fault LED | Notes |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | OFF | Any | Any | Any | Valid (20°C) | **0.00** | **0.00** | OFF | OFF | OFF | All outputs de-energized |
| **2** | ON | NO | Any | 3 (High) | Valid (20°C) | **0.00** | **0.00** | OFF | OFF | OFF | Empty seat interlock |
| **3** | ON | YES | HEAT | 1 (Low) | 20°C (t < 3s) | **0.25** | **0.00** | ON | OFF | OFF | Soft-start phase (25%) |
| **4** | ON | YES | HEAT | 1 (Low) | 20°C (t > 3s) | **0.35** | **0.00** | ON | OFF | OFF | Level 1 steady heat (35%) |
| **5** | ON | YES | HEAT | 2 (Med) | 20°C (t > 3s) | **0.65** | **0.00** | ON | OFF | OFF | Level 2 steady heat (65%) |
| **6** | ON | YES | HEAT | 3 (High) | 20°C (t > 3s) | **0.95** | **0.00** | ON | OFF | OFF | Level 3 steady heat (95%) |
| **7** | ON | YES | HEAT | 1 (Low) | 32.5°C | **0.00** | **0.00** | OFF | OFF | OFF | Thermostatic cutoff ($T \ge 32^\circ\text{C}$) |
| **8** | ON | YES | COOL | 1 (Low) | Any | **0.00** | **0.35** | OFF | ON | OFF | Level 1 quiet ventilation (35%) |
| **9** | ON | YES | COOL | 2 (Med) | Any | **0.00** | **0.65** | OFF | ON | OFF | Level 2 balanced ventilation (65%) |
| **10**| ON | YES | COOL | 3 (High) | Any | **0.00** | **1.00** | OFF | ON | OFF | Level 3 max ventilation (100%) |
| **11**| ON | YES | Any | 0 (OFF) | Any | **0.00** | **0.00** | OFF | OFF | OFF | User turned dial to 0 |
| **12**| ON | YES | HEAT | 3 (High) | 46.0°C | **0.00** | **0.00** | OFF | OFF | **ON** | Over-temperature trip |
| **13**| ON | YES | HEAT | 3 (High) | -2.0°C | **0.00** | **0.00** | OFF | OFF | **ON** | Sensed short-circuit trip |
| **14**| ON | YES | HEAT | 3 (High) | 85.0°C | **0.00** | **0.00** | OFF | OFF | **ON** | Sensed open-circuit trip |
| **15**| ON | YES | HEAT | 3 (High) | 25°C (latched)| **0.00** | **0.00** | OFF | OFF | **ON** | Fault holds after recovery |
| **16**| Cycle| YES | HEAT | 3 (High) | 25°C (cleared)| **0.25** | **0.00** | ON | OFF | OFF | Key cycle clears fault |
| **17**| OFF | YES | HEAT | 1 (Low) | 20°C (t < 10s)| **0.35** | **0.00** | ON | OFF | OFF | Rundown timeout active |
| **18**| OFF | YES | HEAT | 1 (Low) | 20°C (t > 10s)| **0.00** | **0.00** | OFF | OFF | OFF | Rundown timeout expired |

---

## 7. Node Data Dictionary

| Node ID | Type | Role |
| :--- | :--- | :--- |
| `in_ign` | `digital-input` | Senses vehicle switched 12V ignition line. |
| `in_occ` | `digital-input` | Senses cushion occupancy weight pad. |
| `in_cool_mode` | `digital-input` | Cockpit mode selector switch (false = Heat, true = Cool). |
| `in_level` | `analog-input` | Cockpit rotary level dial setting (0.0 to 3.0). |
| `in_temp` | `analog-input` | Cushion NTC thermistor temperature in °C. |
| `timer_ign_timeout` | `tof` | 10.0-second off-delay timer preserving operation after key-off. |
| `gate_power_enable` | `and` | AND gate combining valid power window and seat occupied status. |
| `cmp_sensor_short` | `compare` (`<`) | Detects sensor short circuit (< 0.0°C). |
| `cmp_sensor_open` | `compare` (`>`) | Detects sensor open circuit (> 80.0°C). |
| `cmp_overtemp` | `compare` (`>`) | Detects cushion over-temperature condition (> 45.0°C). |
| `gate_sensor_fault` | `or` | Combines sensor short and open fault signals. |
| `gate_fault_trip` | `or` | Combines sensor faults and over-temperature into master trip signal. |
| `not_ign` | `not` | Inverts ignition to reset fault latch when key is turned OFF. |
| `latch_fault` | `set-reset` | Latches safety fault until ignition key is cycled. |
| `not_fault` | `not` | Inverts latched fault status to provide healthy permissive. |
| `gate_run_enable` | `and` | Master run enable: power valid, occupied, and no fault. |
| `cmp_lvl1` | `compare` (`>=`) | True if LevelSetting >= 0.5 (Level 1 or higher). |
| `cmp_lvl2` | `compare` (`>=`) | True if LevelSetting >= 1.5 (Level 2 or higher). |
| `cmp_lvl3` | `compare` (`>=`) | True if LevelSetting >= 2.5 (Level 3 High). |
| `sel_target_med` | `select` | Selects 37°C if Level >= 2, else 32°C. |
| `sel_target_temp` | `select` | Selects 42°C if Level >= 3, else result of sel_target_med. |
| `sel_heat_duty_med`| `select` | Selects 65% duty if Level >= 2, else 35%. |
| `sel_heat_duty_high`| `select` | Selects 95% duty if Level >= 3, else result of sel_heat_duty_med. |
| `sel_fan_duty_med` | `select` | Selects 65% duty if Level >= 2, else 35%. |
| `sel_fan_duty_high` | `select` | Selects 100% duty if Level >= 3, else result of sel_fan_duty_med. |
| `not_cool_mode` | `not` | Inverts CoolMode to indicate Heating Mode. |
| `gate_heat_selected`| `and` | True if Heating Mode AND Level >= 1. |
| `gate_heat_allowed` | `and` | True if heating selected AND master run enabled. |
| `cmp_temp_satisfied`| `compare` (`<`) | Sensed temperature below setpoint ($T_{\text{seat}} < T_{\text{target}}$). |
| `gate_heater_active`| `and` | True if heating allowed AND temperature below setpoint. |
| `timer_soft_start` | `ton` | 3.0-second timer establishing initial soft-start period. |
| `sel_soft_start` | `select` | Selects full level duty when timer elapses, else 25% soft-start duty. |
| `sel_heater_final` | `select` | Routes soft-start / full heating duty when active, else 0.00. |
| `gate_cool_selected`| `and` | True if Cooling Mode AND Level >= 1. |
| `gate_fan_active` | `and` | True if cooling selected AND master run enabled. |
| `sel_fan_final` | `select` | Routes fan duty when active, else 0.00. |
| `out_heater_pwm` | `pwm-output` | Physical PWM pin commanding heating MOSFET. |
| `out_fan_pwm` | `pwm-output` | Physical PWM pin commanding blower fan speed. |
| `out_heat_indicator`| `digital-output`| Drives Amber/Red cockpit heating indicator LED. |
| `out_cool_indicator`| `digital-output`| Drives Blue cockpit ventilation indicator LED. |
| `out_fault_indicator`| `digital-output`| Drives Red cockpit fault MIL warning LED. |
