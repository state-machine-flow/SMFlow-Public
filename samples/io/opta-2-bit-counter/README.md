# opta-2-bit-counter — 4-Relay Sequential Stepper on Arduino Opta

A 4-state sequential controller designed for the [Arduino Opta](https://docs.arduino.cc/hardware/opta/). Each press of the on-board user button steps through the four mechanical relays in an infinite cycle:

$$\text{All Off (Boot)} \xrightarrow{\text{press}} \text{Relay 1} \xrightarrow{\text{press}} \text{Relay 2} \xrightarrow{\text{press}} \text{Relay 3} \xrightarrow{\text{press}} \text{Relay 4} \xrightarrow{\text{press}} \text{Relay 1} \dots$$

A dedicated reset input turns off all relays and returns the state machine to its initial state.

---

## How It Works

SMFlow graphs are strictly directed acyclic graphs (DAGs) evaluated each scan cycle. Rather than using feedback loops, state is held within native stateful blocks:

```
[ UserButton ] ──▶ [ NOT ] ──┬──▶ [ Toggle Bit0 ] ──┬──▶ [ Falling Edge ] ──▶ [ Toggle Bit1 ]
 (BTN_USER)                  │                      │
                             ▼ (S)                  ▼
                     [ Set/Reset Started ]      [ NOT Bit0 ]
```

1. **Input Inversion**: The Opta's on-board push button (`BTN_USER`) has an internal pull-up resistor and is active-low. An inverting `NOT` gate turns each physical button depression into an active-high rising pulse.
2. **2-Bit Ripple Counter**:
   - `Toggle Bit0` toggles state on each user button press ($0 \to 1 \to 0 \to 1 \dots$).
   - A `Falling Edge` detector watches `Bit0` and pulses `Toggle Bit1`'s clock whenever `Bit0` transitions from $1 \to 0$.
   - Together, $(Bit1, Bit0)$ sequence through the four binary states: `01` $\to$ `10` $\to$ `11` $\to$ `00` $\to$ `01`.
3. **Power-On Boot Latch**:
   - At power-up, both toggles initialize to `(0, 0)`.
   - A `Set/Reset` latch (`Started`) ensures that all relays remain de-energized at boot until the first button press occurs.
4. **1-of-4 State Decoding**:
   - **Relay 1**: $Bit0 \land \overline{Bit1}$ (`01`)
   - **Relay 2**: $\overline{Bit0} \land Bit1$ (`10`)
   - **Relay 3**: $Bit0 \land Bit1$ (`11`)
   - **Relay 4**: $\overline{Bit0} \land \overline{Bit1} \land Started$ (`00`)

---

## Hardware Mapping

| Logical Resource | Terminal / Pin | Type | Notes |
| :--- | :--- | :--- | :--- |
| `UserButton` | `BTN_USER` | Digital Input (`INPUT_PULLUP`) | Front-panel push button |
| `ResetButton` | `I1` | Digital Input | Terminal I1 (+24 VDC signal resets cycle) |
| `Relay1` | `RELAY1` (`D0`) | Digital Output | Relay 1 (mirrored on status LED `LED_D0`) |
| `Relay2` | `RELAY2` (`D1`) | Digital Output | Relay 2 (mirrored on status LED `LED_D1`) |
| `Relay3` | `RELAY3` (`D2`) | Digital Output | Relay 3 (mirrored on status LED `LED_D2`) |
| `Relay4` | `RELAY4` (`D3`) | Digital Output | Relay 4 (mirrored on status LED `LED_D3`) |

> [!NOTE]
> Powering the Arduino Opta via USB-C alone powers the MCU and logic indicators, but an external 12–24 VDC power supply connected to terminals `+` and `-` is required to energize the physical relay coils.

---

## Building and Testing

### Run Graph Tests in the Simulator

The project includes unit tests verifying each state transition and reset behavior:

```bash
smflow test samples/io/opta-2-bit-counter/opta-2-bit-counter.smflow
```

### Build Firmware for Opta

Compile the Arduino sketch binary:

```bash
smflow build samples/io/opta-2-bit-counter/opta-2-bit-counter.smflow
```

### Deploy to Hardware

With the Opta connected via USB-C:

```bash
smflow deploy samples/io/opta-2-bit-counter/opta-2-bit-counter.smflow
```
