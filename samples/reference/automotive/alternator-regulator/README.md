# GM 2020 Duramax Alternator ECU Replacement (Part # 84143541 / 23298275)

An industry reference implementation of an electronic voltage regulator for modern automotive alternators, specifically designed as a standalone **Engine Control Unit (ECU) replacement for the 2020 GM Duramax (L5P 6.6L Turbo-Diesel) alternator (GM Part Numbers 84143541 / 23298275)**.

This application is intended for Duramax engine swaps, classic truck restomods (e.g. C10 / K5 conversions), marine repowers, standalone pulling trucks, and custom vehicles running aftermarket engine management (e.g. Haltech, MoTeC, Holley EFI) that lack native GM Regulated Voltage Control (RVC) alternator logic.

Targeted for the **Raspberry Pi Pico (`rp2040-pico`)** and verifiable in the **SMFlow Simulator (`simulator`)**.

---

## 1. Target Alternator & Application Scope

- **Vehicle Application**: 2020+ Chevrolet Silverado / GMC Sierra 2500HD & 3500HD (6.6L Duramax L5P Turbo-Diesel).
- **OEM Alternator Part Numbers**:
  - **84143541** (Primary 220 A high-output hairpin generator).
  - **23298275** (150 A / 220 A Delco-Remy / Denso hairpin generator).
- **OEM Control System**: GM Regulated Voltage Control (RVC).
- **Physical Connector**: 2-Pin sealed automotive connector:
  - **Pin A (L-Terminal)**: Generator Turn-On Signal / Duty Cycle Command (128 Hz PWM from ECU).
  - **Pin B (F-Terminal)**: Field Monitor / Stator Duty Cycle Feedback (128 Hz PWM from Alternator).
  - **B+ Terminal**: M8 threaded post bolted to positive battery bus.
  - **Ground**: Heavy casing ground through mounting bracket to engine block.

---

## 2. The Duramax Retrofit Problem

When swapping a modern Duramax L5P engine into a classic truck or custom chassis:
1. **Missing ECM / BCM Control**: The factory Duramax alternator does not self-excite like an obsolete 1-wire unit. Without the GM factory ECM sending a 128 Hz PWM command to the L-terminal, the alternator either completely shuts down (0 A output) or operates in an uncontrolled default state that fails to sustain vehicle loads (electric cooling fans, dual battery charging, high-draw accessories).
2. **Fuel Economy vs. Heavy Charging**: Factory GM RVC alternators dynamically toggle between Fuel Economy Mode (~12.68 V) and High Charge Mode (~14.94 V). When running without an OEM BCM, the charging system must be managed to prevent battery sulfation or overvoltage.
3. **High-Torque Starter Protection**: A 6.6L diesel starter draws hundreds of amps during cranking. Energizing a 220 A alternator while cranking creates substantial counter-electromotive torque that drags down cranking speed and drops system voltage. The SMFlow controller guarantees a 2.0s soft-start lockout.

---

## 3. GM RVC Command Specification (L-Terminal)

Per GM engineering documentation, the alternator regulator's target voltage responds linearly to the commanded duty cycle on the **L-terminal** (128 Hz PWM):

| Commanded Duty Cycle | Generator Target Voltage | GM RVC Operating Mode |
| :---: | :---: | :--- |
| **0% – 9%** | *Field De-energized / Standby* | Cranking / Shutdown / Safety Fault |
| **10%** | **11.00 V** | Minimum test floor |
| **20%** | **11.56 V** | Minimum float mode (`DutyFloat` default) |
| **30%** | **12.12 V** | Low maintenance mode |
| **40%** | **12.68 V** | Fuel Economy mode / Thermal Derate (`DutyDerated`) |
| **50%** | **13.25 V** | Battery maintenance mode |
| **60%** | **13.81 V** | Standard float charging |
| **70%** | **14.37 V** | Normal absorption mode |
| **80%** | **14.94 V** | Boost / Heavy recharge mode (`DutyBoost`) |
| **90%** | **15.50 V** | Maximum cold-cranking recovery ceiling |
| **> 90%** | *Saturated / Clamp* | Restricted by software to prevent field coil overheating |

### Linear Transfer Function:
$$V_{\text{target}} = 11.00\text{ V} + 5.625 \times (\text{Duty} - 0.10)$$

---

## 4. Field Feedback Specification (F-Terminal)

The alternator regulator generates a **128 Hz PWM feedback signal** on the **F-terminal**:
- **Normal Operating Range**: Roughly **5% to 99% duty cycle**.
- **Meaning**: Reports the percentage of rotor excitation current currently needed to support the vehicle's electrical load.
- **Abnormal Detection**:
  - Duty cycle < 5% while commanded high indicates rotor open-circuit, belt slippage, or stall.
  - Duty cycle pinned at 100% while system voltage sags indicates an overloaded generator or diode failure.
  - Continuous feedback during zero-command indicates internal shorted regulator transistor.

---

## 5. Decision Flowchart

The controller implements the following control logic:

```text
                     START
                       │
                       ▼
                 IGNITION ON?
                  /         \
                NO           YES
                │             │
                ▼             ▼
               OFF       ENGINE RUNNING?
                            /       \
                          NO         YES
                          │           │
                          ▼           ▼
                       WAIT       REGULATE
                                      │
                              ┌───────┴────────┐
                              │                │
                         Vbat LOW          Vbat HIGH
                              │                │
                              ▼                ▼
                         Increase L       Decrease L
                        (DutyBoost: 80%) (DutyFloat: 20%)
                              │                │
                              └───────┬────────┘
                                      │
                                      ▼
                              Check F feedback
                                      │
                         ┌────────────┼────────────┐
                         │            │            │
                       normal      abnormal    overvoltage
                         │            │          (> 15.6V)
                         ▼            ▼            │
                      continue     DERATE          ▼
                                   (40%)       FIELD OFF
                                               (0% Latch)
```

---

## 6. System Architecture & Block Diagram

```
+-----------------------------------------------------------------------------------------+
|                                SMFlow Controller (RP2040 Pico)                          |
|                                                                                         |
|   [ Ignition (+12V Key) ] --------> GP14 (DI) --+                                       |
|                                                 +--> [ Crank Check & TON 2.0s ]         |
|   [ Engine Run / F-Feed ] --------> GP15 (DI) --+             |                         |
|                                                               v                         |
|   [ Battery Sense (+B) ] ---------> GP26 (AI) -----> [ Hysteresis Comparators ]         |
|                                                               |                         |
|   [ Alternator Temp ] ------------> GP27 (AI) -----> [ Thermal Derate Check ]           |
|                                                               |                         |
|   [ Overvoltage Check ] ---------------------------> [ Fault Latch (SR) ]               |
|                                                               |                         |
|                                                               v                         |
|   [ Field PWM (128 Hz) ] <--------- GP16 (PWM) <--- [ Master Output Multiplexer ]       |
|    (To Duramax Pin A: L)                                                                |
|                                                                                         |
|   [ Charge Warning Lamp ] <------- GP17 (DO)  <--- [ Bulb-Check & Failure Logic ]       |
|                                                                                         |
|   [ Fault MIL Lamp ] <------------- GP18 (DO)  <--- [ Safety Trip Indicator ]           |
+-----------------------------------------------------------------------------------------+
```

---

## 7. Hardware Wiring & I/O Definitions

| Logical Resource | Physical Pin (`rp2040-pico`) | Duramax 84143541 / 23298275 Signal | Hardware Circuitry & Wiring |
| :--- | :--- | :--- | :--- |
| `Ignition` | `GP14` | Switched +12V Key (Run/Start) | Level-shifted to 3.3V logic via $10\text{ k}\Omega / 3.3\text{ k}\Omega$ divider and 3.3V Zener clamp. |
| `EngineRun` | `GP15` | Engine Run / Pin B (F-Terminal) | Stator / F-feedback line or tachometer pulse conditioned to 3.3V logic. |
| `BatterySense` | `GP26` | Alternator +B Post / Battery Positive | Precision $47\text{ k}\Omega / 10\text{ k}\Omega$ divider (0–18V scaled to 0–3.15V at pin). |
| `AlternatorTemp`| `GP27` | Alternator Housing Temperature | NTC thermistor mounted to rear bearing housing of 84143541 alternator. |
| `FieldPwm` | `GP16` | **Pin A (L-Terminal)** | 128 Hz PWM output driving an open-drain N-FET (2N7002) with 1 k$\Omega$ pull-up to +12V. |
| `ChargeWarning` | `GP17` | Instrument Cluster Battery Lamp | High-side automotive smart switch driving dash "BATTERY" / "ALT" light. |
| `FaultIndicator`| `GP18` | Diagnostic MIL / LED | Low-side driver illuminating LED upon latched overvoltage or thermal shutdown. |

---

## 8. State Machine & Regulation Strategy

1. **OFF**: Key is OFF. Field PWM is 0.00%. Quiescent battery drain is 0 mA.
2. **WAIT (Startup & Bulb Check)**: Key is ON, engine stopped or cranking. Field PWM is locked at 0.00% by the 2.0s startup delay (`timer_startup`), preventing starter motor drag on the 6.6L Duramax. The dash warning lamp is ON for bulb verification.
3. **REGULATE (Normal Closed-Loop)**:
   - When $V_{bat} < 14.15\text{ V}$ (`VTargetLow`), the controller commands **Increase L** (`DutyBoost = 0.80`, corresponding to **14.94 V** in the GM table).
   - When $V_{bat} > 14.25\text{ V}$ (`VTargetHigh`), the controller commands **Decrease L** (`DutyFloat = 0.20`, corresponding to **11.56 V** in the GM table).
   - The 100 mV hysteresis deadband ($14.15\text{ V} \to 14.25\text{ V}$) eliminates PWM chatter, while rotor field inductance ($L/R \approx 70\text{ ms}$) naturally smooths excitation current into steady DC.
4. **DERATING**: If alternator housing temperature reaches $105^\circ\text{C}$ (`TempDerateLimit`), the field command is clamped to **40% (`DutyDerated`)**, commanding **12.68 V** (GM Fuel Economy Mode) to prevent diode pack failure in cramped Duramax engine bays.
5. **FAULT (Safety Shutdown)**:
   - Overvoltage ($V_{bat} > 15.60\text{ V}$) or extreme temperature ($T > 130^\circ\text{C}$) trips a `set-reset` latch.
   - Field PWM is immediately forced to **0.00% (FIELD OFF)**.
   - Both warning and fault indicators illuminate.
   - The fault remains latched until the ignition key is cycled OFF.

---

## 9. Simulation & Automated Testing

The automated test suite ([`alternator-regulator.smtest`](file:///F:/repos/ctacke/SMFlow-Public/samples/reference/automotive/alternator-regulator.smtest)) runs against the SMFlow native simulator and verifies:

1. **Initial Power-Off**: With ignition OFF, all outputs remain de-energized.
2. **Dashboard Bulb-Check**: Ignition ON with engine stopped turns ON the charge warning lamp with zero field PWM.
3. **Cranking Interlock**: Engine turning over holds field excitation at 0.00% during the 2.0s startup delay.
4. **Transition to Boost**: When 2.0s elapses, field jumps to 0.80 (14.94 V command) and charge lamp extinguishes.
5. **Float Transition**: Voltage rising above 14.25 V switches excitation to 0.20 float (11.56 V command).
6. **Hysteresis Deadband**: Fluctuations between 14.16 V and 14.24 V hold the previous regulation state.
7. **Electrical Load Step**: Voltage dropping to 14.10 V triggers immediate recovery boost (0.80).
8. **Boundary Precision**: Verifies exact behavior at 14.14 V vs 14.15 V.
9. **Thermal Derating**: Heating to 105°C clamps field duty to 0.40 (12.68 V).
10. **Thermal Recovery**: Cooling below 105°C restores full 0.80 boost capability.
11. **Overvoltage Trip**: 15.65 V latches fault, zeroes field, and turns on fault/warning lamps.
12. **Thermal Trip**: 131°C trips emergency thermal shutdown.
13. **Key Cycling Recovery**: Switching ignition OFF clears the latched fault and allows clean restart.
14. **Ignition Removal**: Switching key OFF during full charging immediately kills field excitation.
15. **Engine Stall**: Loss of engine rotation resets the startup timer and de-energizes the field.

---

## 10. CLI Commands for Testing and Building

```bash
# Validate against Raspberry Pi Pico and the Simulator
smflow validate samples/reference/automotive/alternator-regulator.smflow --target rp2040-pico
smflow validate samples/reference/automotive/alternator-regulator.smflow --target simulator

# Run the 15 automated test cases in the simulator
smflow test samples/reference/automotive/alternator-regulator.smflow samples/reference/automotive/alternator-regulator.smtest

# Emit native C++ firmware for the RP2040 Pico
smflow build samples/reference/automotive/alternator-regulator.smflow --target rp2040-pico --emit-only
```
