# SMFlow Fundamentals — a hands-on lab series

A self-paced series for engineers who already ship control systems and have never seen SMFlow.

**Who this is for.** You write ladder, structured text, or firmware in C. You know what a scan
cycle is, you have opinions about interrupt latency, and you are suspicious of visual programming
tools because the ones you have met generated unreviewable code or needed a runtime on the box.
This series is written for you. It assumes nothing about SMFlow and everything about control.

**What you will end up with.** A working mental model of how a graph becomes C++, and the muscle
memory to build, simulate, test, deploy, and debug a real flow on real hardware.

---

## How the series works

A concepts tour, then twelve hands-on labs, then a capstone. Each lab is 15–25 minutes and produces
something that runs.

**[Lab 0](lab-00-concepts/) is the exception** — it builds nothing. It is a 25-minute read that
establishes the model: what a scan is, what a task is, what a node is, how variables and I/O and
targets and peripherals fit together, and what SMFlow does and does not guarantee. It is written
for both PLC and Arduino backgrounds and maps every term onto something you already know. Start
there unless you strongly prefer to learn by doing, in which case start at Lab 1 and come back when
a word stops making sense.

Every hands-on lab follows the same shape:

| Section | Purpose |
|---|---|
| **The problem** | A control problem stated the way a plant engineer would state it |
| **What you'll learn** | Three to five bullets, concrete |
| **Build it** | Numbered steps, editor-first, CLI equivalents shown |
| **Run it** | Simulate, then (where applicable) deploy |
| **Look at the code** | The generated C++ for what you just built — every lab does this |
| **Break it** | A deliberate mistake, the diagnostic it produces, and the fix |
| **On your own** | One unguided extension, with a solution in `solution/` |
| **What just happened** | The concept, named and explained, now that you have seen it work |

Each lab's project is named after the lab — `lab-01.smflow`, `lab-02.smflow` — so your editor's
recent-projects list stays readable as you work through the series. Exercise solutions live in
`solution/` beside each lab. Screenshots live in `<lab>/images/`; slots not yet captured show a
placeholder describing the shot.

The "look at the code" section is not optional garnish. It is the series' central argument: the
graph is source code, the C++ is the object of review, and nothing is hiding.

### Hardware

**Labs 1–7 and 11 need no hardware at all.** They run in the desktop simulator.

Labs 8, 9, 10, and 12 use a **Raspberry Pi Pico** (~$10) on a breadboard. The full parts list is in
[`PARTS.md`](PARTS.md). Where a lab touches a pin, it also shows the same graph retargeted to an
Arduino Opta and an ESP32-S3 without changing a single node — that retarget *is* the lesson.

### Prerequisites

- SMFlow installed — [installation guide](../docs/getting-started/installation.md)
- The `smflow` CLI on your `PATH` — [CLI guide](../docs/guide/cli.md)
- A C++ toolchain for the targets you build (per-lab, called out where needed)
- The Free tier is enough through Lab 7; Labs 8+ exceed the free node limit in places and note it

---

## Lab 0 — How SMFlow works

**Reading, 25 min. No hardware, no building.**

The product tour and the vocabulary, before you touch anything.

- Where you're coming from — a PLC↔Arduino↔SMFlow translation table
- SMFlow is a compiler, not a runtime
- **The scan** — snapshot-and-commit, and why mid-scan pin reads don't exist
- **Tasks** — normal, init, interrupt; the tick as GCD of all periods; cooperative scheduling
- **Nodes, ports, properties, types** — and why there are no implicit conversions
- **Variables** — shared state, atomicity, torn read-modify-write, retention
- **I/O** — logical names versus pins, and the per-target binding table
- **Targets** — profiles as data; the simulator as a target like any other
- **Peripherals** — the device model, async operations, scan budgets
- **The toolchain** — editor, CLI, build report, diagnostic codes
- **Guaranteed vs. measured vs. not claimed**
- Seven self-check questions with answers

→ [Read Lab 0](lab-00-concepts/)

---

## Part I — How a flow actually runs

The goal of Part I is to replace "it's like ladder logic, I guess" with an accurate model.

### [Lab 1 — Your first flow, and the C++ it becomes](lab-01-first-flow/)
`Motor = !StartButton`. Three nodes. Build it, simulate it, then open the generated `main.cpp` and
read it line by line. No `Node`, no `Graph`, no `ExecuteNode`, no interpreter — just a `while` loop
and a boolean.

- Graph → project → IR → C++ → native binary, as a picture and as files on disk
- `smflow validate`, `smflow build`, `smflow simulate`
- Why the editor is not the runtime
- **Break it:** delete a wire, read the validation error, fix it
- **Concept:** ahead-of-time compilation; the editor is a code generator, not a VM

*Sample basis:* `samples/basics/not-gate`

### [Lab 2 — The scan cycle](lab-02-scan-cycle/)
A conveyor interlock with two independent output chains. Ten nodes collapse into two expressions,
and five of them vanish entirely.

- Read-inputs → evaluate → write-outputs, visible in the generated code
- Execution order is a compile-time topological sort of the dataflow
- Layout has no semantics — proved with `diff`, not asserted
- The declaration-order tiebreak, and why it is harmless
- **Break it:** a feedback loop (`SMF0007`), two writers on one input (`SMF0006`)
- **Concept:** determinism is a property of the rule, not of uniqueness

### [Lab 3 — Tasks and periods](lab-03-tasks/)
Safety logic at 10 ms, reporting at 250 ms, and an init task that runs before either.

- Task kinds: normal, init, interrupt — and what an init task replaces
- The scheduler tick as the GCD of every period, in the generated code
- Why a wire cannot cross tasks, and shared variables with generated critical sections
- What SMFlow *guarantees* (logical order) versus *measures* (execution time) versus
  *does not claim* (hard real-time)
- **Break it:** cross-task wire (`SMF0015`), zero period (`SMF0009`), two init tasks (`SMF0034`)
- **Concept:** determinism is about order, not latency. Say it out loud.

### [Lab 4 — Types, ports, and why there are no silent conversions](lab-04-types/)
A tank level sensor, a threshold alarm, and a formatted console line. The first non-boolean type.

- `float32` through a graph, and what it becomes in C++
- Properties versus ports, including nodes whose port types derive from a property
- Fixed-capacity text buffers and compile-time format templates
- `.iomap`, and why a serial endpoint is a binding rather than a node
- **Break it:** four wrong connections, four diagnostics (`SMF0004`, `SMF0003`, `SMF0014`)
- **Concept:** exact-match typing; conversion is a node you place, visible to a reviewer.

---

## Part II — Building real logic

### Lab 5 — State: latches, counters, and edges
A start/stop station with a seal-in. Then the same thing with `set-reset`, then with `toggle`.

- `set-reset`, `toggle`, `counter`, `rising-edge`, `falling-edge`
- Where state lives in the generated C++ (spoiler: a `static` struct, not a heap)
- Scan-to-scan persistence versus power-cycle persistence (foreshadows Lab 11)
- **On your own:** add a cycle counter that survives a stop

*Sample basis:* `samples/logic/motor-interlock`, `samples/timing/stopwatch`

### Lab 6 — Timers
`ton` and `tof` against a real control problem: a motor that must run 3 seconds after the stop
button, and must not start until the guard has been closed for 500 ms.

- On-delay and off-delay semantics, precisely
- How a timer is implemented in the emitted C++ — tick counts, not wall clocks
- Timer resolution and its relationship to task period
- **Break it:** a timer with a period shorter than its task's scan period

*Sample basis:* `samples/timing/start-delay`

### Lab 7 — Variables, and the debug loop
Named shared variables, `variable-read` / `variable-write` / `variable-update`, and using the serial
console as your print-debugger.

- Shared variables as the seam between tasks
- `to-text` and format templates
- `serial-tx` to a host console; watching values live
- Stepping and inspecting in the simulator
- **Concept:** the debug workflow — simulate, inspect, narrow, then go to hardware

*Sample basis:* `samples/basics/variable-compare`, `samples/basics/serial-debug`

---

## Part III — Real hardware

### Lab 8 — Your first deploy (Pico)
Take the Lab 5 interlock, bind it to physical pins, and flash it.

- The `.iomap` file: logical names on one side, physical pins on the other
- Why pin binding is not in the graph
- `smflow build --target rp2040-pico`, then `smflow deploy`
- Reading the build manifest and the artifact
- **Break it:** bind to a pin the profile does not expose; read the refusal

*Sample basis:* `samples/io/pico-interlock`, `samples/io/pico-latch`

### Lab 9 — One graph, three boards
The same project, retargeted to Pico, ESP32-S3, and Arduino Opta. Diff the generated code.

- Hardware profiles — what a target declares about itself
- What changes in the emitted C++ and what does not
- `smflow targets`, `smflow describe-target`
- **Concept:** target portability is a property of the compiler, not of a HAL you maintain

*Sample basis:* `samples/io/opta-interlock`

### Lab 10 — Analog, PWM, and sound
Read a pot, drive a PWM output, make a piezo chirp. The point is the non-boolean I/O path.

- `analog-input`, `analog-output`, `pwm-output`, `tone-output`
- Scaling and the absence of implicit conversion, again, in anger
- Per-target analog resolution differences

*Sample basis:* `samples/io/pwm-piezo`, `samples/io/piezo-double-beep`

---

## Part IV — Systems concerns

### Lab 11 — Persistence that survives power loss
A machine-cycle counter and a configurable setpoint that come back after a reboot.

- Persistent shared variables; `persist-save`, `persist-clear`, `persist-status`
- The backing store per target: ESP32 NVS, AVR EEPROM, RP2040 reserved flash, Linux file store
- Write endurance, and why persistence is explicit rather than automatic
- Async storage operations and their scan budget (see `docs/timing.md` §4)
- **Break it:** save every scan; read the budget warning

*Sample basis:* `samples/applications/persistent-counter`

### Lab 12 — A peripheral end to end (SSD1306 + a sensor)
Put a live reading on a display over I²C.

- The device model: you configure a part, not a raw bus
- I²C buses in the hardware profile; addressing
- Asynchronous device nodes — `async-peripheral-run`, busy/done, and why a driver never blocks
  the scan
- A driver either drives the part or refuses to build (ADR 0045) — no half-working peripherals
- **On your own:** swap the sensor for a different one from the catalog

*Sample basis:* `samples/peripherals/ssd1306-text`, `samples/peripherals/apds-9960`

### Capstone — A complete machine
Guard interlock, two-speed motor with timed ramp, cycle counter persisted to flash, operator
display, and a fault latch. Deployed to a Pico. Specified as a requirements document, not as
steps — you build it.

Includes a `.smtest` suite so you can check your own work.

---

## Deliberately not in this series

Covered in a follow-on series, not here:

- CAN bus and signal-level messaging
- LoRa / SX1262 radio links
- Modbus server and SCADA integration
- `.smtest` graph-level testing in depth (used in the capstone, not taught)
- The MCP server and AI-assisted authoring
- Interrupt tasks
- Writing your own device plugin

---

## Video production

Each lab maps to one long-form YouTube video (12–20 min) and 2–3 shorts. Scripts, shot lists, and
B-roll notes live in [`production/`](production/). See
[`production/README.md`](production/README.md) for the format and the per-lab status board.

---

## Status

| Lab | Content | Screens | Script | Recorded |
|---|---|---|---|---|
| 0 Concepts | ✅ | 0/14 | ✅ | — |
| 1 First flow | ✅ | 0/17 | ✅ | — |
| 2 Scan cycle | ✅ | 0/6 | — | — |
| 3 Tasks and periods | ✅ | 0/8 | — | — |
| 4 Types and ports | ✅ | 0/7 | — | — |
| 5 State | — | — | — | — |
| 6 Timers | — | — | — | — |
| 7 Variables and debug | — | — | — | — |
| 8 First deploy | — | — | — | — |
| 9 One graph, three boards | — | — | — | — |
| 10 Analog and PWM | — | — | — | — |
| 11 Persistence | — | — | — | — |
| 12 Peripheral end to end | — | — | — | — |
| Capstone | — | — | — | — |
