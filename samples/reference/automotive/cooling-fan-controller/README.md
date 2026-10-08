# Standalone Electric Cooling Fan Controller (EF-ECU)

An industry reference implementation of an electronic cooling fan control unit for automotive retrofits and restomods, replacing inefficient mechanical engine-driven clutch fans with modern dual electric cooling fans (e.g. Spal, Derale, Flex-A-Lite, or OEM dual-fan assemblies from C6 Corvette, Ford Contour, or GM LS/LT trucks).

Designed for classic muscle car restomods, pro-touring builds, custom hot rods, truck repowers, and aftermarket EFI conversions (e.g. Holley Sniper/Terminator, Haltech, MoTeC, FiTech) requiring standalone multi-stage temperature regulation, A/C condenser cooling, vehicle speed ram-air lockouts, and post-shutdown after-run cooling.

Targeted for the **Raspberry Pi Pico (`rp2040-pico`)** and verifiable in the **SMFlow Simulator (`simulator`)**.

---

## 1. Application Scope & The Hot-Rod Cooling Problem

In high-performance classic cars and hot rods, cooling high-horsepower crate engines (e.g. Chevy 350 SBC, 454 BBC, GM LS3/LT4, Ford Coyote 5.0, Chrysler Gen-III Hemi) in tight engine bays is notoriously challenging:

1. **Mechanical Clutch Fan Deficiencies**: Factory belt-driven mechanical fans draw between 15 and 28 horsepower at high RPM, create aerodynamic buffeting, and pull minimal airflow at low engine idle speeds in stop-and-go traffic—precisely when heat transfer demands are highest.
2. **Severe Electrical Inrush Current**: High-flow aftermarket electric fans (e.g. dual 12-inch or 14-inch Spal brushed fans) draw 25 A to 35 A continuous each. When switched directly across 12V through standard thermal switches, their locked-rotor inrush current exceeds **60 A to 90 A**. Energizing both fans simultaneously drops system voltage, stalls the alternator, stresses the idle air control (IAC), and melts relay sockets.
3. **Highway Ram-Air Interference**: Above highway cruise speeds (typically > 40–45 mph / 65–70 km/h), vehicle forward speed naturally forces high-volume ram air through the radiator core. Running electric fans at 75 mph provides zero cooling benefit, causes aerodynamic drag across fan blades, accelerates motor brush wear, and wastes alternator amperage.
4. **Air Conditioning Condenser Heat Load**: Activating the cockpit A/C causes head pressure in the front-mounted condenser to spike instantly. Without immediate forced airflow across the condenser core, A/C high-pressure relief switches trip before the engine coolant warms up.
5. **Post-Shutdown "Heat Soak"**: When an engine is switched off after hard driving, the water pump stops circulating coolant, but thermal mass in the iron/aluminum cylinder heads radiates heat into stagnant radiator coolant. Temperatures commonly spike 10°C to 20°C within 3 to 5 minutes after shutdown, resulting in boiling coolant and radiator cap venting.

The SMFlow **Electric Cooling Fan Controller** solves these challenges with deterministic multi-stage PWM regulation, hysteresis deadbands, vehicle speed lockouts, starter motor cranking protection, post-shutdown rundown timing, and fail-safe sensor diagnostics.

---

## 2. System Architecture & Control Strategy

```
+-----------------------------------------------------------------------------------------+
|                        SMFlow Cooling Fan Controller (RP2040 Pico)                       |
|                                                                                         |
|   [ Ignition (+12V Key) ] --------> GP14 (DI) --+                                       |
|                                                 +--> [ Starter Crank & Bulb Check ]     |
|   [ Engine Run (Tach/Alt) ] ------> GP15 (DI) --+            │                          |
|                                                              ▼                          |
|   [ Coolant Temp (CTS) ] ---------> GP26 (AI) -----> [ Hysteresis Comparators ]         |
|                                                              │                          |
|   [ Vehicle Speed (VSS) ] --------> GP27 (AI) -----> [ Highway Ram-Air Cutoff ]         |
|                                                              │                          |
|   [ A/C Request Switch ] ---------> GP13 (DI) -----> [ Condenser Airflow Logic ]        |
|                                                              │                          |
|                                                              ▼                          |
|   [ Primary Fan PWM (0–100%) ] <--- GP16 (PWM) <--- [ Multi-Stage PWM Mux ]             |
|   [ Secondary Fan Relay ] <-------- GP17 (DO)  <--- [ High-Stage Output Gate ]          |
|   [ Dash Warning Lamp ] <---------- GP18 (DO)  <--- [ Bulb-Check / Fault Latch ]        |
+-----------------------------------------------------------------------------------------+
```

### Staged Multi-Output Architecture

- **Fan 1 (Primary Fan — Progressive PWM)**:
  - Driven by GP16 at 0.00 (Off), 0.50 (50% low-noise soft stage), or 1.00 (100% full speed).
  - Handles initial thermostatic demand, low-speed A/C condenser airflow, and post-shutdown after-run cooling.
  - Limits electrical bus shock by never engaging at 100% during cold starts.
- **Fan 2 (Secondary Fan — High Stage Relay)**:
  - Driven by GP17 digital output to energize a 40 A high-current relay.
  - Engaged only when coolant exceeds Stage 2 temperature or during Emergency Mode.
- **Warning Indicator (Dash MIL / Overheat Lamp)**:
  - Driven by GP18 digital output to illuminate instrument cluster "COOLANT / FAN" warning lamp.

---

## 3. Calibrated Setpoints & Operating Modes

| Parameter Variable | Calibrated Value | Function |
| :--- | :---: | :--- |
| `TempStage1On` | **88.0°C (190.4°F)** | Primary fan cut-in setpoint (thermostat full-open temperature). |
| `TempStage1Off` | **83.0°C (181.4°F)** | Primary fan cut-out setpoint providing **5.0°C hysteresis deadband**. |
| `TempStage2On` | **96.0°C (204.8°F)** | Secondary fan cut-in setpoint for heavy thermal loading. |
| `TempStage2Off` | **91.0°C (195.8°F)** | Secondary fan cut-out setpoint providing **5.0°C hysteresis deadband**. |
| `TempEmergency` | **106.0°C (222.8°F)** | Emergency overheat limit forcing both fans to 100% and warning lamp ON. |
| `TempCritical` | **110.0°C (230.0°F)** | Critical alarm threshold triggering latched fan failure warning. |
| `TempAfterRunThresh` | **92.0°C (197.6°F)** | Minimum coolant temperature required to trigger post-shutdown cooldown. |
| `TempSensorMin` | **0.0°C (32.0°F)** | Plausibility floor; readings below indicate shorted NTC wiring. |
| `TempSensorMax` | **130.0°C (266.0°F)** | Plausibility ceiling; readings above indicate open circuit or unplugged harness. |
| `SpeedCutoff` | **70.0 km/h (~44 mph)** | Highway speed threshold where vehicle ram-air suppresses Stage 1 fans. |
| `DutyLow` | **0.50 (50%)** | Progressive PWM duty cycle for Stage 1, A/C, and after-run cooling. |
| `DutyHigh` | **1.00 (100%)** | Maximum PWM duty cycle for Stage 2 and emergency overheat modes. |
| `DutyOff` | **0.00 (0%)** | Zero duty cycle when cooling is inactive. |

---

## 4. Control Logic & Operating States

### 1. Off State (`Ignition == false`, Engine Cold)
All outputs remain fully de-energized. Quiescent current draw is negligible (< 100 µA).

### 2. Ignition ON, Engine Cranking / Stopped (Bulb Check & Starter Protection)
When the driver switches the ignition key to ON/RUN without starting the engine (`Ignition == true`, `EngineRun == false`):
- Fan 1 and Fan 2 are **locked OFF** to preserve 100% battery capacity for the high-compression starter motor.
- The dash `WarningOutput` illuminates as an instrument cluster **bulb-check verification**.

### 3. Normal Closed-Loop Regulation (Engine Running)
When the engine is running (`Ignition == true`, `EngineRun == true`):
- **Warming Up (< 88.0°C)**: Both fans remain OFF.
- **Stage 1 Cut-In (88.0°C to 96.0°C)**: Fan 1 engages at **50% PWM (`DutyLow`)**. As temperature drops, Stage 1 latch holds until temperature falls below **83.0°C**, preventing cycling chatter.
- **Stage 2 Cut-In (>= 96.0°C)**: Fan 1 ramps to **100% PWM (`DutyHigh`)** and Fan 2 relay energizes. Both fans remain at maximum until temperature cools below **91.0°C**, dropping back to Stage 1.

### 4. Cockpit A/C Request Override
When cockpit air conditioning is turned on (`AcRequest == true`):
- Fan 1 is immediately commanded to **50% PWM** below highway speed, guaranteeing continuous airflow across the front condenser core.
- If engine coolant rises into Stage 2, Fan 2 energizes normally alongside Fan 1.

### 5. Highway Ram-Air Lockout
When cruising at highway speeds (`VehicleSpeed >= 70.0 km/h` / ~44 mph):
- Vehicle forward motion forces sufficient airflow through radiator and condenser fins.
- Stage 1 coolant temperature demand and A/C fan requests are automatically **suppressed**, saving electrical alternator power and reducing motor wear.
- If coolant reaches Stage 2 (96.0°C) or Emergency Overheat (106.0°C), ram-air lockout is **overridden**, delivering maximum forced cooling.

### 6. Emergency Overheat & Sensor Fault Fail-Safe
- **Critical Overheat (>= 106.0°C)**: Both Fan 1 (100%) and Fan 2 are forced ON, and `WarningOutput` illuminates.
- **Sensor Fault (Open > 130°C or Short < 0°C)**: The controller assumes worst-case failure, forces both fans to 100% full blast, and illuminates the warning lamp.

### 7. Fan Failure Detection
If coolant temperature continues to climb past **110.0°C (`TempCritical`)** while Stage 2 cooling is commanded active, a latched fan failure alarm trips (`latch_fan_fail`). The warning indicator remains locked ON until the driver cycles the ignition switch.

### 8. Post-Shutdown After-Run Cooling
When the driver switches the ignition key OFF:
- If the engine was operating hot (`CoolantTemp >= 92.0°C`), an off-delay timer (`timer_after_run`, TOF) runs Fan 1 at **50% PWM** for up to **30.0 seconds**.
- Fan 2 remains locked OFF to prevent heavy battery discharge.
- If coolant drops below **83.0°C** before the 30-second timer expires, Fan 1 shuts off immediately to preserve battery charge.

---

## 5. Hardware Wiring & Physical Pin Assignments

| Logical Resource | RP2040 Pico Pin | Direction | Channel | Automotive Interface & Circuitry |
| :--- | :---: | :---: | :---: | :--- |
| `Ignition` | **GP14** | Input | Digital | Switched +12V Key (RUN/ACC). 10 k$\Omega$ / 3.3 k$\Omega$ divider with 3.3V Zener clamp. |
| `EngineRun` | **GP15** | Input | Digital | Tachometer pulse, alternator stator (W-terminal), or fuel pump relay +12V signal. |
| `AcRequest` | **GP13** | Input | Digital | Cockpit A/C compressor clutch 12V feed or trinary pressure switch line (divided to 3.3V). |
| `CoolantTemp` | **GP26** (ADC0) | Input | Analog | GM Delphi 2-pin CTS NTC thermistor with precision 2.49 k$\Omega$ 1% pull-up to 3.3V. |
| `VehicleSpeed` | **GP27** (ADC1) | Input | Analog | Transmission VSS frequency-to-voltage converter or 0–5V GPS speedometer module. |
| `Fan1Pwm` | **GP16** | Output | PWM | 20 kHz PWM signal driving solid-state power module (e.g. C6 Corvette / Ford PWM fan module). |
| `Fan2Relay` | **GP17** | Output | Digital | Logic-level N-FET (2N7002 / IRLZ44N) driving coil of standard 40 A SPST automotive relay. |
| `WarningOutput` | **GP18** | Output | Digital | Low-side driver or smart high-side switch powering dash "CHECK COOLANT" lamp. |

---

## 6. Automated Test Suite

The test suite ([`cooling-fan-controller.smtest`](file:///F:/repos/ctacke/SMFlow-Public/samples/reference/automotive/cooling-fan-controller/cooling-fan-controller.smtest)) runs against the native SMFlow simulator:

1. **Power-Off Inactive**: Verifies all outputs remain de-energized with key OFF.
2. **Dashboard Bulb Check**: Confirms warning lamp illuminates with zero fan duty when key is ON and engine is stopped.
3. **Engine Running Normal**: Verifies zero fan duty while engine warms up below 88°C.
4. **Stage 1 Cut-In**: Confirms Fan 1 engages at 50% PWM when coolant reaches 88.5°C.
5. **Stage 1 Hysteresis**: Verifies Fan 1 holds 50% PWM as coolant fluctuates between 88°C and 83°C.
6. **Stage 1 Cut-Out**: Confirms Fan 1 stops when coolant drops below 83.0°C.
7. **Stage 2 Cut-In**: Confirms Fan 1 ramps to 100% and Fan 2 relay energizes at 96.5°C.
8. **Stage 2 Hysteresis**: Verifies both fans remain energized while cooling down between 96°C and 91°C.
9. **Stage 2 Cut-Out**: Confirms secondary fan turns off and Fan 1 drops to 50% below 91.0°C.
10. **A/C Request in Traffic**: Confirms Fan 1 engages at 50% PWM when A/C is requested at 20 km/h.
11. **Highway Ram-Air Lockout**: Confirms fans are suppressed at 75 km/h despite A/C and warm coolant.
12. **Emergency Overheat Lockout Override**: Confirms emergency overheat (106.5°C) overrides highway speed lockout and illuminates warning lamp.
13. **Sensor Open-Circuit Fail-Safe**: Confirms sensor open circuit (> 130°C) triggers 100% fans and warning lamp.
14. **Sensor Short-Circuit Fail-Safe**: Confirms sensor short circuit (< 0°C) triggers 100% fans and warning lamp.
15. **Fan Failure Alarm Latch**: Confirms temperature climbing to 110.5°C during Stage 2 latches fan failure warning.
16. **Ignition Key Reset**: Confirms cycling ignition switch clears latched fan failure alarm.
17. **Hot Engine Key-Off After-Run**: Confirms shutting down at 94°C initiates Fan 1 50% cooldown.
18. **After-Run Timer Timeout**: Confirms after-run timer cleanly shuts down Fan 1 after 30 seconds.
19. **Battery-Saving Cooldown Cutoff**: Confirms after-run Fan 1 shuts off early if coolant drops below 83°C.
20. **Cool Engine Key-Off**: Confirms key-off below 92°C does not trigger after-run fan.

---

## 7. CLI Commands for Testing and Building

```bash
# Set development license entitlement
export SMFLOW_LICENSE_SIMULATE=pro

# 1. Validate flow against Raspberry Pi Pico and the Simulator
smflow validate samples/reference/automotive/cooling-fan-controller/cooling-fan-controller.smflow --target rp2040-pico
smflow validate samples/reference/automotive/cooling-fan-controller/cooling-fan-controller.smflow --target simulator

# 2. Run the 20 automated test cases in the simulator
smflow test samples/reference/automotive/cooling-fan-controller/cooling-fan-controller.smflow samples/reference/automotive/cooling-fan-controller/cooling-fan-controller.smtest

# 3. Emit native C++ firmware for the RP2040 Pico
smflow build samples/reference/automotive/cooling-fan-controller/cooling-fan-controller.smflow --target rp2040-pico --emit-only
```
