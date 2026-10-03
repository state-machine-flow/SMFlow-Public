# Lab 0 — "How SMFlow works"

**Long-form target:** 14–16 min · **Shorts:** 3 · **Hardware:** none

**The one thing a viewer must leave with:** the graph is compiled source code, it runs in scans,
and every unfamiliar word in this product maps onto something they already know.

**Format note.** This is the only episode that isn't a build-along. It's animation and diagrams
over narration, with short cuts to real artifacts (the editor, a build report, generated code) to
keep it from floating. Resist the urge to make it a slide deck with a voice over it — every concept
gets *shown* at least once.

---

## Cold open (0:00 – 0:30)

> `[SCREEN]` Split screen, both halves moving. Left: a ladder rung in a PLC IDE. Right: an Arduino
> `loop()` in the Arduino IDE.

**[VO]** If you build control systems, you're one of these two people.

**[BEAT]**

> `[SCREEN]` Both halves slide away. Center: a small SMFlow graph, three nodes.

**[VO]** SMFlow borrows from both of you. Which means roughly eighty percent of what you already
know transfers directly — and there's a twenty percent that'll trip you up if nobody tells you
about it.

**[VO]** This episode is the twenty percent. No building today. Just the model.

> `[ON-SCREEN TEXT]` SMFlow Fundamentals · Lab 0 — Concepts

---

## Where you're coming from (0:30 – 2:00)

> `[SCREEN]` The translation table, built one row at a time as each is spoken. Don't show all of it
> at once — it reads as homework.

**[VO]** Here's the whole translation table. I'm not going to make you memorize it — it's in the
written lab — but I want you to see how short it is.

**[VO]** A scan is a scan, if you're a PLC person. If you're an Arduino person, a scan is one pass
of `loop()`.

**[VO]** A task is a program with a cycle time. Or it's a timed slice of `loop()` that you'd
otherwise hand-roll with `millis()`.

**[VO]** An init task is your first-scan bit. Or it's `setup()`.

**[VO]** An interrupt task is an interrupt OB. Or it's `attachInterrupt`.

**[VO]** A node is an instruction or a function block. Or it's an expression.

> `[BEAT]`

**[VO]** Same ideas. Different words. The only genuinely new thing is what the tool does with them
— so let's start there.

---

## 1. SMFlow is a compiler (2:00 – 4:00)

> `[SCREEN]` The pipeline, drawn left to right, one box at a time.
> ```
> graph → project → typed IR → validation → lowering → C++ → native binary
> ```

**[VO]** The graph you draw is source code. Not a configuration, not a script, not a picture of
your program — source code. It gets parsed, type-checked, lowered to an intermediate
representation, and translated into C++. Ahead of time. On your machine.

> `[SCREEN]` The last box pulses. Everything before it greys out.

**[VO]** That native binary is what ships. And here's the part worth being precise about: there is
no SMFlow on the controller.

> `[ON-SCREEN TEXT]` No interpreter · No runtime · No .NET, Node, Python, JVM

**[VO]** No interpreter. No scripting engine. No graph structure anywhere in memory. No runtime
library of ours. The controller never finds out that a graph existed.

> `[SCREEN]` Quick cut — generated `application.cpp`, two lines of logic, full frame. Two seconds.
> Don't explain it. Just show it.

**[VO]** Lab 1 is mostly about reading that file. For now, two things follow from it.

**[VO]** One: the editor is not the runtime. It's an authoring tool. The CLI does the builds, and
your build server never installs the editor.

**[VO]** Two: the generated code is the deliverable. It goes in your repo and through your review
process, in front of engineers who've never heard of this product.

---

## 2. The scan (4:00 – 7:00) — **the core section**

> `[SCREEN]` Animated scan diagram. Inputs snapshot → logic → outputs commit → wait. Loop it
> several times at a readable speed.

**[VO]** A SMFlow program doesn't run continuously. It runs in scans. Read all the inputs,
evaluate the logic, write all the outputs. Wait for the period. Do it again.

> `[ON-SCREEN TEXT, PLC side]` You already know this. Keep your intuition.

**[VO]** If you're a PLC person — that's the scan cycle, including the I/O image, and your
instincts are correct.

> `[ON-SCREEN TEXT, Arduino side]` Two differences. One will surprise you.

**[VO]** If you're an Arduino person, it's `loop()`, with two differences.

**[VO]** First, it runs on a fixed period. Not as fast as the CPU can go — every ten milliseconds,
or whatever you declare.

**[VO]** Second, and this is the one: I/O is snapshotted.

### Snapshot and commit

> `[SCREEN]` Zoom into the diagram. An input pin toggles mid-scan. The logic block visibly does
> **not** react. Next scan boundary, the snapshot picks it up, and the logic reacts.
> Replay this animation twice.

**[VO]** Watch this. The pin changes two milliseconds into the scan.

**[BEAT]**

**[VO]** The logic doesn't see it. It's reading a snapshot taken at the top of the scan, not the
pin. It picks up the change on the *next* scan.

**[VO]** Same on the way out. You write to the output image, and the whole image goes to the pins
once, at the bottom. Write an output twice in one scan and only the last value ever reaches
copper.

> `[SCREEN]` Real generated `main.cpp` while loop, full frame. Highlight `ReadInputs` then
> `WriteOutputs`.

**[VO]** And that's not a diagram, that's the generated code. Read inputs. Run the task. Write
outputs. Sleep.

**[VO]** Why do it this way? Because it makes one scan a pure function of its inputs and its
retained state.

> `[ON-SCREEN TEXT]` Same inputs + same state → same outputs. Always.

**[VO]** Same inputs, same state, same outputs — every time, on any target. That's what makes the
program testable. It's what makes the simulator worth trusting. And it's what stops two tasks
running at different rates from disagreeing about what the inputs were.

**[VO]** Arduino folks: yes, you're losing something. You can't poll a pin mid-loop and react in
microseconds any more. If you genuinely need that, there's an interrupt task — but measure before
you reach for it.

---

## 3. Tasks (7:00 – 9:15)

> `[SCREEN]` A task card with its four fields filling in: Name, Period, Priority, Budget.

**[VO]** A task is a unit of execution with a rule for when it runs. Every node lives in exactly
one. There's no loose logic.

**[VO]** Name, which becomes the generated function. Period, which is always explicit — never
silently defaulted. Priority, for tasks that come due together. And an optional budget, which the
runtime checks against.

### Three kinds

> `[SCREEN]` Three cards.

**[VO]** Normal repeats forever on a period. That's almost everything you'll write.

**[VO]** Init runs once, before the first scan. Seeding variables, putting a peripheral in a mode,
latching an output safe. That's your `setup()`. It's also your first-scan bit — if you've been
writing "IF FirstScan THEN", that logic has a home now.

**[VO]** And interrupt runs on an edge, outside the scan, for a pulse too short for your period to
catch. It compiles to a real ISR, so what it's allowed to contain is restricted and the compiler
enforces it. We don't use them in this series. Sharp tool, and the fundamentals don't need it.

### The tick

> `[SCREEN]` Timeline animation: a 10 ms task and a 25 ms task on a shared 5 ms tick. Marks fire
> where each is due. Let it run for several cycles.

**[VO]** Here's a detail I like. Declare a ten millisecond task and a twenty-five millisecond task
— what rate does the scheduler run at?

**[BEAT]**

**[VO]** Five. The greatest common divisor of every period you declared.

> `[SCREEN]` Real generated `main.cpp` — `constexpr std::uint64_t kTickMs = 5;` then the two
> modulo checks.

**[VO]** And there it is in the generated code. Tick of five, one check per task. Which means both
tasks fire exactly on their own period, with no rounding. A scheduler at any other rate would drift
against at least one of them.

**[VO]** One more thing. Scheduling is cooperative and single-threaded. Tasks run to completion;
nothing preempts anything. So a long scan in a low-priority task *will* delay a high-priority one
that comes due during it. The diagnostics count that. Nothing prevents it.

---

## 4. Nodes, ports, types (9:15 – 11:00)

> `[SCREEN]` A single node, zoomed. Label the input ports, the output ports, then the inspector
> panel beside it.

**[VO]** A node is one operation. It has input ports, output ports, and properties.

**[VO]** The port-versus-property distinction matters. A port is dataflow — a value arriving over a
wire, possibly different every scan. A property is configuration — a timer's preset, a comparison's
operator. Fixed at compile time, baked into the generated code.

> `[SCREEN]` Wiring animation showing each rule as it's stated, including a refused connection.

**[VO]** Wires carry one value, output port to input port. An input takes at most one wire — two
sources for one input doesn't mean anything, so the editor just won't let you. An output can feed
as many inputs as you like. A wire can't cross between tasks. And no cycles — a combinational loop
is an error, not an oscillator.

### Types

> `[SCREEN]` The type list. Then: dragging a `float32` output toward an `int32` input. The
> connection is refused — show the actual editor behavior.

**[VO]** Values are typed. Bool, int32, uint32, float32, float64, duration, bytes.

**[VO]** And assignment is exact match only. No implicit conversion, no numeric promotion. You
cannot wire a float into an int input and have the compiler quietly truncate it for you.

> `[ON-SCREEN TEXT]` Conversion is a node you place. Visible in the graph.

**[VO]** If you want a conversion, you place a conversion node, and it's right there in the graph
where a reviewer can see it.

**[VO]** My favorite example: `duration` is a separate type from the integers, specifically so you
can't wire a counter into a timer preset. That's an entire bug class deleted by the type system
instead of caught in review.

**[VO]** This is stricter than C. It's stricter than most PLC languages. It is also the number one
source of "why won't it let me connect this" in your first hour — and the answer is always the
same. It's telling you those two things aren't the same kind of thing.

---

## 5. Variables and I/O (11:00 – 13:00)

> `[SCREEN]` Two tasks side by side, a shared variable between them. Animate a write from one and
> a read from the other.

**[VO]** Wires carry values within a task, within a scan. Shared variables carry values across
tasks and across scans.

**[VO]** You declare it with a name, a type, an initial value. And you reach it with nodes — read,
write, and update — not with a wire. Because a wire between two tasks at different rates would have
to carry a timing rule that the picture doesn't show you. A node puts the access right where it
happens.

> `[SCREEN]` Real generated `LoadShared_Enable()` with `EnterCritical` / `ExitCritical`.

**[VO]** Every access is atomic. There's your critical section, generated for you.

**[VO]** But atomicity is per access. Read, add one, write back is *two* accesses with a gap in
between, and another task can get in there. That's what the `variable-update` node is for — the
whole read-modify-write as one operation. And the validator warns you when your graph has the torn
shape.

> `[ON-SCREEN TEXT]` Arduino: this is `volatile` + `noInterrupts()`, applied for you.

### Logical I/O

> `[SCREEN]` The binding diagram. One logical name, arrows out to three different boards.

**[VO]** Now I/O, and this is one of my favorite design decisions in the product.

**[VO]** The graph never names a pin. It names a logical resource — `StopButton`. The binding to
an actual pin lives beside the graph, in a table, per target.

**[VO]** Opta, that's I2. Pico, gpio17. Simulator, a virtual point.

**[VO]** Nothing in the graph changes when the board changes. Only which row of that table gets
read. That's why Lab 9 — the same graph on three different boards — takes five minutes instead of
being a port.

---

## 6. Targets and peripherals (13:00 – 14:45)

> `[SCREEN]` `smflow targets` run live in a terminal.

**[VO]** A target is a board, a toolchain, and a hardware profile. The profile declares what the
board actually has — pins, what each can do, analog resolution, buses, storage. It's data, not
code. No board is hard-coded into the compiler.

**[VO]** And the simulator is a target like any other. It compiles your flow to a host binary and
runs it against virtual I/O and a simulated clock. It is not an interpreter and not a second
implementation of your logic — which is exactly why you can trust what it tells you, and also why
you need a C++ compiler installed even for the labs with no hardware.

> `[SCREEN]` A peripheral declaration, then the display node that uses it, then a quick shot of a
> real SSD1306 showing text.

**[VO]** Peripherals: you declare the device, not the bus traffic. Here's an SSD1306. Now I've got
a node that writes a line of text to it. I never composed an I²C transaction. I never picked a
register address.

**[VO]** Three rules. A driver either drives the part or refuses to build — there's no
half-supported device. Device operations are asynchronous and never block the scan, because an I²C
write takes milliseconds and your task runs every ten. And the buses themselves live in the
hardware profile, because which bus exists on which pins is a property of the board, not of your
program.

---

## 7. Guaranteed, measured, not claimed (14:45 – 16:00) — **do not cut this**

> `[SCREEN]` Three columns, filled in one at a time. Clean, serious typography.

**[VO]** Last thing, and it's the most important ninety seconds in this episode.

> `[ON-SCREEN TEXT]` GUARANTEED — deterministic logical execution

**[VO]** Guaranteed: deterministic logical execution. Order is computed at compile time. The
generated code is a flat, linear sequence of statements. Same inputs and state, same outputs, every
time. Build the same project twice and the C++ is byte-identical.

> `[ON-SCREEN TEXT]` MEASURED — execution time

**[VO]** Measured: execution time. Every task keeps counters — scan duration, budget overruns,
deadline misses. Those are observations, taken on the target, after the fact.

> `[ON-SCREEN TEXT]` NOT CLAIMED — hard real-time

**[BEAT]**

**[VO]** Not claimed: hard real-time. SMFlow does not promise a deadline will be met. It runs as an
ordinary process or a cooperative superloop — not under an RTOS with admission control. If your
application needs a provable worst-case response, this tool does not give you one, and you should
know that now and not at commissioning.

**[VO]** The rule that falls out of it: design for the order, measure the time, and never confuse
the two.

**[VO]** And one footnote — in simulation, those overrun counters are structurally zero, because a
simulated scan takes no simulated time. Timing numbers only mean something on hardware.

---

## Next (16:00 – 16:20)

**[VO]** That's the model. Next lab we build the smallest program that can exist, and then we open
up the C++ it generated and read every line of it.

**[VO]** There's a self-check at the bottom of the written lab — seven questions. If you can answer
them, you're ready.

> `[ON-SCREEN TEXT]` Lab 1 — Your first flow
> Written lab: [link]

---

# Shorts

## Short 1 — "The one thing Arduino devs get wrong" (50 s)

**Claim:** I/O is snapshotted; mid-scan pin changes aren't seen until the next scan.

> `[0:00–0:08, shot for vertical]` Arduino `loop()` on screen, a `digitalRead` highlighted.

**[VO]** If you write Arduino, you think of this as reading a pin. In SMFlow, it isn't. And this
trips up every single person coming from embedded C.

> `[0:08–0:28]` The scan animation: pin toggles mid-scan, logic does not react, next boundary it
> does. Play it twice.

**[VO]** Inputs are snapshotted once, at the top of the scan. Your logic reads the snapshot, not
the pin. So when this input changes two milliseconds in —

**[BEAT]**

**[VO]** — nothing happens. Not until the next scan.

> `[0:28–0:50]`

**[VO]** Feels like a limitation. It's the opposite. It makes one scan a pure function of its
inputs, which is what makes the program testable and makes the simulator worth trusting.

**[VO]** PLC folks: you already knew this. It's the I/O image.

---

## Short 2 — "What tick rate?" (40 s)

**Claim:** The scheduler tick is the GCD of all task periods.

> `[0:00–0:08, vertical]` Two task cards: 10 ms and 25 ms.

**[VO]** Quick one. You declare a ten millisecond task and a twenty-five millisecond task. What
rate does the scheduler actually run at?

> `[0:08–0:18]` Beat. Let them guess.

**[VO]** It's not ten. It's not twenty-five.

> `[0:18–0:32]` Reveal: `constexpr std::uint64_t kTickMs = 5;` in the real generated main.cpp.

**[VO]** Five. The greatest common divisor of every period in the project.

> `[0:32–0:40]` Timeline animation of both firing exactly on their periods.

**[VO]** Which means both tasks fire exactly on their own period, with zero rounding. Any other
rate would drift against at least one of them.

---

## Short 3 — "The slide nobody puts in a sales deck" (45 s)

**Claim:** SMFlow is explicit that it does not provide hard real-time.

> `[0:00–0:10, vertical]` The three-column card, blank headers.

**[VO]** Every industrial tool should have this slide. Almost none of them do.

> `[0:10–0:20]` Fill column one.

**[VO]** Guaranteed: deterministic logical execution. Same inputs, same outputs, every time,
byte-identical builds.

> `[0:20–0:28]` Fill column two.

**[VO]** Measured: execution time. Counters on the target. Observations, after the fact.

> `[0:28–0:45]` Fill column three. Hold on it.

**[VO]** Not claimed: hard real-time. SMFlow will not promise you a deadline. It's a cooperative
loop, not an RTOS with admission control.

**[BEAT]**

**[VO]** If you need a provable worst-case response, you should know that now — not at
commissioning. That's in our docs, in those words.
