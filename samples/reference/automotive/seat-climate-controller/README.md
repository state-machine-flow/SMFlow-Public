# Automotive Retrofit Climate-Controlled Seat Module (CCSM)

An industry reference implementation of a standalone **Climate-Controlled Seat Module (CCSM)** for automotive retrofit heated and ventilated seats (e.g. Recaro, Sparco, Katzkin, and OEM luxury seat transplants from Cadillac, Lincoln, Ford F-150 Platinum, and Porsche).

Designed for automotive restomods, overland expedition builds, classic muscle car conversions, and custom vehicle builds that lack factory Body Control Module (BCM) or LIN-bus seat climate networks.

Targeted for the **Raspberry Pi Pico (`rp2040-pico`)** and verifiable in the **SMFlow Simulator (`simulator`)**.

---

## 1. Target Hardware & Application Scope

- **Vehicle Application**: Standalone retrofit or engine swap / interior restomod running aftermarket or OEM climate seats.
- **Supported Seat Hardware**:
  - **Heating Elements**: High-power carbon-fiber or nichrome resistive wire pads (cushion and lumbar backrest), driven via high-side MOSFET PWM.
  - **Ventilation Fans**: Brushless 12V centrifugal blowers / axial fans ducted through cushion perforations, driven via speed PWM.
  - **Temperature Sensor**: Embedded 10 k$\Omega$ NTC thermistor or linear analog temperature sensor reporting cushion surface temperature in °C.
  - **Occupancy Sensor**: Seat weight / pressure pad switch in bottom cushion.
- **Cockpit User Interface**:
  - `CoolMode` digital toggle/rocker switch (false = Heating Mode, true = Ventilation/Cooling Mode).
  - `LevelSetting` analog rotary dial or multi-position step switch (0.0 = OFF, 1.0 = Low, 2.0 = Medium, 3.0 = High).
  - Status LEDs: Amber/Red `HeatIndicator`, Blue `CoolIndicator`, and Red `FaultIndicator`.

---

## 2. The Retrofit Problem

Modern climate seats from OEM luxury vehicles or high-end aftermarket manufacturers feature integrated heating mats and ducted ventilation blowers. In original vehicles, these actuators are governed by proprietary LIN-bus or CAN-bus commands originating from the central Body Control Module (BCM) and HVAC head unit.

When retrofitting these seats into custom vehicles, hot rods, or classic trucks:
1. **Missing BCM / Digital Bus**: Without the factory CAN/LIN messages, the seat heaters and blower fans remain completely inert. Direct 12V hardwiring is dangerous: unregulated heating elements can overheat leather cushions, cause burns, or catch fire.
2. **Current Inrush & Thermal Shock**: Cold carbon-fiber heating elements exhibit low initial resistance, drawing up to 15 A when energizing. An uncontrolled step to 100% duty cycle creates electrical bus dips and thermal shock. The SMFlow controller provides an automatic **3.0s soft-start ramp** (limited to 25% duty) before stepping up to the commanded power level.
3. **Open / Short Sensor Failure Protection**: Seat thermistor wiring is subject to flexing, pinch points in seat reclining mechanisms, and connector wear. A crushed wire grounded to the steel frame or an unplugged harness would fool standard controllers into full continuous heating. This controller detects short (< 0.0°C) and open (> 80.0°C) faults and trips an emergency latched shutdown.
4. **Battery Rundown Prevention**: Heating elements rapidly drain vehicle starting batteries if left running with the engine stopped. The controller features an **ignition-off rundown timeout (10.0s)** that allows brief accessory transitions but guarantees complete automatic shutdown once the timer expires.
5. **Occupancy Interlock**: Heating or ventilating an empty seat wastes electrical power and risks hotspot buildup. The controller interlocks all actuators with the seat cushion occupancy sensor.

---

## 3. Climate Modes, Setpoints & Power Levels

The controller supports three distinct operating levels plus OFF across both heating and cooling modes:

### Heating Mode (`CoolMode == false`)

| Setting Level | User Level | Target Temp Setpoint | Soft-Start Duty (0–3 s) | Full Commanded Duty | Cockpit Indicator |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **0.0** | **OFF** | — | 0% | 0% | OFF |
| **1.0** | **Low** | **32.0°C (89.6°F)** | 25% | **35% PWM** | Heat LED ON |
| **2.0** | **Medium** | **37.0°C (98.6°F)** | 25% | **65% PWM** | Heat LED ON |
| **3.0** | **High** | **42.0°C (107.6°F)** | 25% | **95% PWM** | Heat LED ON |

*Note: Heating duty automatically cuts off when `SeatTemp >= TargetTemp` (thermostatic closed-loop regulation) and re-engages when temperature dips below setpoint.*

### Ventilation / Cooling Mode (`CoolMode == true`)

| Setting Level | User Level | Blower Fan Duty Cycle | Acoustic / Airflow Profile | Cockpit Indicator |
| :---: | :---: | :---: | :---: | :---: |
| **0.0** | **OFF** | **0%** | Fan stopped | OFF |
| **1.0** | **Low** | **35% PWM** | Whisper quiet continuous air circulation | Cool LED ON |
| **2.0** | **Medium** | **65% PWM** | Balanced forced ventilation | Cool LED ON |
| **3.0** | **High** | **100% PWM** | Maximum forced convection cool-down | Cool LED ON |

---

## 4. Diagnostics & Safety Protection

| Condition | Threshold | System Action | Latch Behavior |
| :--- | :---: | :--- | :--- |
| **Over-Temperature Cutoff** | `SeatTemp > 45.0°C` | Emergency shutdown of heater and fan. Fault LED energized. | Latched until Ignition is cycled OFF. |
| **Sensor Short-Circuit** | `SeatTemp < 0.0°C` | Immediate actuator shutdown. Prevents runaway heating from grounded sensor line. | Latched until Ignition is cycled OFF. |
| **Sensor Open-Circuit** | `SeatTemp > 80.0°C` | Immediate actuator shutdown. Detects unplugged harness or broken wire. | Latched until Ignition is cycled OFF. |
| **Seat Unoccupied** | `SeatOccupied == false` | Forces heater and fan PWM to 0.00%. | Automatic restore when occupant sits. |
| **Ignition Off Rundown** | `Ignition == false` (> 10s) | Shuts down all outputs to preserve 12V battery. | Automatic restore when key is turned ON. |

---

## 5. Control Flow & Architecture

```text
                       [Ignition Input]
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
             [TOF Timer: 10s]     [Invert: not_ign]
                    │                   │
                    ▼                   │
            [Power Window Valid]        │
                    │                   │
      ┌─────────────┴─────────────┐     │
      ▼                           ▼     │
[Seat Occupied?]           [Safety Faults]
  (Interlock)             - Over-Temp (> 45°C)
      │                   - Sensor Short (< 0°C)
      │                   - Sensor Open (> 80°C)
      │                           │
      ▼                           ▼
[Healthy Enable] ◄─────── [Fault Latch (SR)] ◄── Reset via key-off
      │
      ├───────────────────────────────┐
      │ (Heating Mode)                │ (Cooling Mode)
      ▼                               ▼
[Thermostatic Compare]        [Fan Level Duty Selection]
(SeatTemp < TargetTemp?)      - Level 1: 35%
      │                       - Level 2: 65%
      ▼                       - Level 3: 100%
[Soft-Start Timer (3.0s)]             │
- Initial 3s: 25% Duty                ▼
- Steady: 35% / 65% / 95%         [Fan PWM Out]
      │
      ▼
[Heater PWM Out]
```

---

## 6. Physical Hardware Pin Mapping (Raspberry Pi Pico)

| Logical Resource | Direction | Channel | Pico Pin | Description | External Circuitry |
| :--- | :---: | :---: | :---: | :--- | :--- |
| `Ignition` | Input | Digital | **GP14** | Vehicle Switched +12V (RUN/ACC) | 12V-to-3.3V optocoupler or resistor divider (10k / 3.3k) with TVS diode. |
| `SeatOccupied` | Input | Digital | **GP15** | Cushion Pressure Mat Sensor | Normally-open contact pulling to GND with internal 3.3V pull-up. |
| `CoolMode` | Input | Digital | **GP13** | Heat/Cool Selector Switch | Cockpit SPST toggle switch pulling GP13 to 3.3V (High = Cool, Low = Heat). |
| `LevelSetting` | Input | Analog | **GP26 (ADC0)** | Multi-Position Level Dial | 10k potentiometer or 4-position resistive divider (0V, 1V, 2V, 3V). |
| `SeatTemp` | Input | Analog | **GP27 (ADC1)** | Seat Cushion Thermistor | 10k NTC thermistor in voltage divider with 10k precision reference resistor. |
| `HeaterPwm` | Output | PWM | **GP16** | Heating Element Gate Command | Open-drain MOSFET driver / high-side automotive P-FET switch (e.g. Infineon PROFET). |
| `FanPwm` | Output | PWM | **GP17** | Ventilation Fan Speed PWM | 25 kHz / low-frequency PWM driving brushless seat blower speed terminal. |
| `HeatIndicator`| Output | Digital | **GP18** | Heating Active Indicator | 2N7002 driving cockpit switch Amber/Red LED through current-limiting resistor. |
| `CoolIndicator`| Output | Digital | **GP19** | Cooling Active Indicator | 2N7002 driving cockpit switch Blue LED through current-limiting resistor. |
| `FaultIndicator`| Output | Digital | **GP20** | Safety Diagnostic Indicator | 2N7002 driving cockpit Red MIL warning LED. |

---

## 7. State Machine & Safety Logic

1. **OFF**: Vehicle key is OFF and rundown timeout has elapsed. All actuators and indicators are de-energized (0 mA quiescent current).
2. **OCCUPANCY INHIBIT**: Key is ON, but seat is unoccupied (`SeatOccupied == false`). Actuators remain de-energized to prevent heating an empty seat.
3. **HEAT REGULATION**:
   - `CoolMode == false`, `SeatOccupied == true`, `LevelSetting >= 1.0`.
   - If `SeatTemp < TargetTemp`, heating energizes.
   - For the first 3.0 seconds, `timer_soft_start` clamps the heating duty to **25% (`DutySoftStart`)**, preventing bus voltage dip.
   - After 3.0 seconds, duty steps to full level setpoint: **35% (Low)**, **65% (Med)**, or **95% (High)**.
   - When cushion temperature reaches the level target (32°C, 37°C, or 42°C), heater duty turns OFF until temperature drops.
4. **VENTILATION COOLING**:
   - `CoolMode == true`, `SeatOccupied == true`, `LevelSetting >= 1.0`.
   - Blower fan runs continuously at commanded duty: **35% (Low)**, **65% (Med)**, or **100% (High)**.
   - Heater is locked OFF.
5. **SAFETY FAULT LATCH**:
   - Over-temperature (`SeatTemp > 45.0°C`), sensor short (`SeatTemp < 0.0°C`), or sensor open (`SeatTemp > 80.0°C`) triggers `latch_fault`.
   - Heater PWM and Fan PWM are immediately zeroed.
   - `FaultIndicator` illuminates.
   - Fault remains latched even if temperature normalizes, until the driver cycles the vehicle ignition key OFF and ON.
6. **RETAINED ACCESSORY POWER (TIMEOUT)**:
   - When the ignition key is switched OFF, `timer_ign_timeout` (`tof`, 10.0s) preserves power window.
   - If key remains OFF for > 10.0 seconds, all actuators and lights turn OFF.

---

## 8. Simulation & Automated Testing

The automated test suite ([`seat-climate-controller.smtest`](./seat-climate-controller.smtest)) verifies 19 distinct functional scenarios against the SMFlow simulator:

1. **Initial Power-Off**: All outputs de-energized when ignition is OFF.
2. **Unoccupied Seat**: Empty seat inhibits heating despite ignition ON and High level selected.
3. **Soft-Start Initiation**: Heating level 1 starts with 25% duty cycle.
4. **Soft-Start Transition**: Level 1 steps up to 35% duty after 3.0s delay.
5. **Level 2 Heating**: Medium heat level steps up to 65% duty after soft-start.
6. **Level 3 Heating**: High heat level steps up to 95% duty after soft-start.
7. **Thermostatic Cutoff**: Reaching target temperature de-energizes heater duty.
8. **Cooling Level 1**: Drives low fan duty (35%) with zero heater output.
9. **Cooling Level 2**: Drives medium fan duty (65%).
10. **Cooling Level 3**: Drives maximum fan duty (100%).
11. **Level 0 Off**: Setting dial to 0 de-energizes both heater and fan.
12. **Over-Temperature Cutoff**: Exceeding 45°C latches fault and kills all actuators.
13. **Sensor Short Circuit**: Sensed temp < 0°C latches fault.
14. **Sensor Open Circuit**: Sensed temp > 80°C latches fault.
15. **Fault Persistence**: Latched fault holds even when temperature returns to normal.
16. **Key Cycle Recovery**: Cycling ignition key OFF and ON clears fault when sensor is healthy.
17. **Ignition Rundown Timeout**: Operation preserved during 10s post-ignition rundown delay.
18. **Timeout Expiry**: Rundown timeout expiration de-energizes all power.
19. **Occupant Departure**: Passenger leaving seat immediately cuts heater duty.

---

## 9. CLI Commands for Testing and Building

```bash
# Validate against Raspberry Pi Pico and the Simulator
smflow validate samples/reference/automotive/seat-climate-controller.smflow --target rp2040-pico
smflow validate samples/reference/automotive/seat-climate-controller.smflow --target simulator

# Run the 19 automated test cases in the simulator
smflow test samples/reference/automotive/seat-climate-controller.smflow samples/reference/automotive/seat-climate-controller.smtest

# Emit native C++ firmware for the RP2040 Pico
smflow build samples/reference/automotive/seat-climate-controller.smflow --target rp2040-pico --emit-only
```
