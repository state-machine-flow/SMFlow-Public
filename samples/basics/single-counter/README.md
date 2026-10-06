# single-counter — event-driven counting in SMFlow

A minimal, canonical representation of the IEC 61131-3 **Counter** block.

In controls engineering, counting discrete physical events (parts on a conveyor, encoder pulses, button presses) requires tracking transitions across scans. The `counter` node encapsulates internal count state, edge detection, preset comparison, and reset dominance into a single block.

```
CountInput  ──▶ CU ┌─────────┐
                   │ Counter │ Q ──▶ BatchDone
ResetInput  ──▶ R  └─────────┘
```

---

## How It Works

* **Edge-Triggered (`CU`)**: Each transition of `CountInput` from `false` $\to$ `true` increments the internal count (`CV`). Holding `CountInput` high across multiple scans counts exactly once.
* **Preset Evaluation (`Q`)**: When the accumulated count reaches the configured `presetCount` (configured to 5 in this sample), the `Q` output transitions to `true` and remains latched true.
* **Reset Dominance (`R`)**: Asserting `ResetInput` clears the count back to 0 and forces `Q` false immediately. If `CU` and `R` are both asserted in the same scan cycle, `R` takes precedence.

---

## Wiring and Mappings

| Logical Resource | Direction | Opta | Pico | Description |
| :--- | :--- | :--- | :--- | :--- |
| `CountInput` | Input | `I1` | `GP16` | Pulse signal / Part sensor |
| `ResetInput` | Input | `I2` | `GP15` | Reset pushbutton |
| `BatchDone` | Output | `RELAY1` (`D0`) | `GP25` (LED) | Target reached indicator |

---

## Running the Sample

### Run Simulator Tests
Verify the counter logic with the included graph tests:

```bash
smflow test samples/basics/single-counter/single-counter.smflow
```

### Build for Simulator or Hardware
Build the simulator executable:

```bash
smflow build samples/basics/single-counter/single-counter.smflow --target simulator
```

Or compile for hardware (e.g. Arduino Opta or Raspberry Pi Pico):

```bash
smflow build samples/basics/single-counter/single-counter.smflow --target opta
```
