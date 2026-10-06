# step-sequencer — sequential multi-stage process control

A classic industrial **Step Sequencer** (or Drum Controller / Phase Sequencer).

In automated processes (such as chemical batching, automated washing, part curing, or machine startup sequences), operations progress through a defined order of timed phases:

$$\text{Idle} \xrightarrow{\text{Start}} \text{Stage 1 (2s)} \xrightarrow{\text{Timer 1}} \text{Stage 2 (3s)} \xrightarrow{\text{Timer 2}} \text{Sequence Complete}$$

Pressing the **Stop** button at any time immediately aborts execution and resets all stages back to Idle.

```
StartButton ──▶ S ┌───────────┐
                  │ Set/Reset │ Q ──┬──▶ TON Timer1 (2s) ──┬──▶ TON Timer2 (3s) ──▶ SequenceDone
StopButton  ──▶ R └───────────┘     │      │               │      │
                                    ▼      ▼               ▼      ▼
                                  [ Stage 1 Gate ]       [ Stage 2 Gate ]
                                         │                      │
                                         ▼                      ▼
                                       Stage1                 Stage2
```

---

## How It Works

* **Master Run Latch**: A `set-reset` latch holds the running state once `StartButton` is pressed.
* **Cascaded On-Delay Timers (`TON`)**:
  * `Timer1` measures Stage 1 duration (2,000 ms).
  * `Timer2` measures Stage 2 duration (3,000 ms), starting only after `Timer1` has elapsed.
* **Phase Decoding (Acyclic DAG)**:
  * **Stage 1 Active**: `Running AND NOT Timer1.Q` (Active from start until Timer 1 completes).
  * **Stage 2 Active**: `Timer1.Q AND NOT Timer2.Q` (Active while Timer 1 is done but Timer 2 is still running).
  * **Sequence Done**: `Timer2.Q` (Asserts once all stages have completed).
* **Safe Abort**: Asserting `StopButton` resets the latch, which drops `IN` on all downstream timers, immediately de-energizing all stages and resetting elapsed times to zero.

---

## Wiring and Mappings

| Logical Resource | Direction | Opta | Pico | Description |
| :--- | :--- | :--- | :--- | :--- |
| `StartButton` | Input | `I1` | `GP16` | Cycle start pushbutton |
| `StopButton` | Input | `I2` | `GP15` | Cycle stop / E-stop pushbutton |
| `Stage1` | Output | `RELAY1` (`D0`) | `GP25` (LED) | Stage 1 active (e.g. Fill valve) |
| `Stage2` | Output | `RELAY2` (`D1`) | `GP13` | Stage 2 active (e.g. Agitate motor) |
| `SequenceDone` | Output | `RELAY3` (`D2`) | `GP14` | Process complete indicator |

---

## Running the Sample

### Run Simulator Tests
Run the deterministic graph tests to verify the timing transitions and abort logic:

```bash
smflow test samples/timing/step-sequencer/step-sequencer.smflow
```

### Build for Simulator or Hardware
Compile for the desktop simulator:

```bash
smflow build samples/timing/step-sequencer/step-sequencer.smflow --target simulator
```

Or compile for industrial hardware targets:

```bash
smflow build samples/timing/step-sequencer/step-sequencer.smflow --target opta
```
