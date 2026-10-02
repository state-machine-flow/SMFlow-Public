# Lab 1 — "Your first flow, and the C++ it becomes"

**Long-form target:** 16–18 min · **Shorts:** 3 · **Hardware:** none

**The one thing a viewer must leave with:** SMFlow is a compiler. The thing on the controller is
ordinary C++ with no graph in it.

---

## Cold open (0:00 – 0:25)

> `[SCREEN]` Black. Then, full-frame, syntax-highlit, nothing else:
>
> ```cpp
> void MainTask(IO& io)
> {
>     const bool startButton = io.StartButton;
>
>     io.Motor = !startButton;
> }
> ```

**[VO]** This is C++ that a visual programming tool wrote.

**[BEAT]**

> `[SCREEN]` Cut to the three-node graph in the editor, held for two seconds.

**[VO]** From this.

**[BEAT]**

> `[SCREEN]` Back to the C++.

**[VO]** No interpreter. No runtime. No graph structure anywhere on the controller. If that sounds
like a claim worth checking — good. Let's check it.

> `[ON-SCREEN TEXT]` SMFlow Fundamentals · Lab 1

---

## The problem (0:25 – 1:45)

> `[SCREEN]` Talking head, or a plain title card over a slow pan of a control panel.

**[VO]** If you build control systems, you've been pitched a visual programming tool before. And
you've probably seen what came out the other end — technically C, obviously machine-generated. A
graph in an array. A dispatch loop. A switch statement over node IDs.

**[VO]** You can't put that through firmware review. You can't debug it at three in the morning
when the line is down. So you went back to ladder, or structured text, or you just wrote the
firmware yourself.

**[BEAT]**

**[VO]** SMFlow takes a different position: the graph is source code, and the C++ is the object of
review. Over this series we're going to test that claim pretty hard. Today we start with the
smallest program that can test it at all.

> `[ON-SCREEN TEXT]` Motor = !StartButton

**[VO]** A motor runs whenever a normally-closed stop button isn't pressed. One contact, one coil.
You could write it in your sleep. That's the point — the program is trivial, so there's nowhere for
the toolchain to hide.

---

## Build (1:45 – 7:30)

### New project

> `[SCREEN]` Terminal, 18pt.
> ```
> smflow new lab-01.smflow --name "Lab 01 - First Flow"
> ```
> Then open it in the editor. Empty canvas.

**[VO]** A new project has one task in it. It's called Main, it runs every ten milliseconds, and
it's empty. Every node you place has to live in some task — there's no loose logic floating around
— so the task exists before anything else does.

**[VO]** That'll matter in Lab 3 when we have more than one.

### Three nodes

> `[SCREEN]` Drag Digital Input from the I/O palette. Rename to `StartButton` in the inspector.
> Drag NOT from Logic. Drag Digital Output, rename to `Motor`. Real-time, no cuts.

**[VO]** Digital Input. Logic, NOT. Digital Output.

**[VO]** I'm naming these — StartButton and Motor — and the names aren't cosmetic. They become
logical I/O points, which is what you'll later bind to actual pins, and they show up verbatim in
the generated code. Watch for them later.

> `[ON-SCREEN TEXT]` Names matter. Node IDs don't.

**[VO]** The node IDs underneath — start, not1, motor — those are just editor bookkeeping. They
never affect what the program means.

### Wiring

> `[SCREEN]` Drag port to port. Both wires.

**[VO]** Output port to input port. StartButton's value into NOT. NOT's output into Motor.

**[VO]** Ports are typed, and the IDs are case-sensitive and different per node. Digital Input
gives you `value`. NOT gives you `in` and `out`. When you're not sure, hover it — don't guess.

### Validate

> `[SCREEN]` ```
> smflow validate lab-01.smflow
> Lab 01 - First Flow: valid.
> ```

**[VO]** Valid. And I want to be clear about what that word is doing, because it's not a lint pass
you can override. An invalid graph doesn't produce code at all. Not partial code, not best-effort
code with a warning. No code. We'll break it on purpose in a few minutes and you'll see.

---

## Run (7:30 – 9:30)

> `[SCREEN]` ```
> smflow simulate lab-01.smflow
> ```
> Simulator panel. Toggle StartButton. Motor responds. Toggle back. Let this run for a good
> fifteen seconds without narration over the top of it.

**[VO]** Start button on — motor off. Start button off — motor on.

**[BEAT]**

**[VO]** One thing about that simulator that's worth knowing now. It is not interpreting your
graph. It compiled your flow to a real binary and it's running that binary against a virtual I/O
table and a simulated clock.

> `[ON-SCREEN TEXT]` The simulator runs the generated code. Not a model of it.

**[VO]** Which is why you need a C++ compiler installed even for a lab with no hardware in it. It's
also why what you see in the simulator is worth trusting. There's no second implementation that
can drift from the real one.

---

## The code (9:30 – 14:00) — **the hero section**

> `[SCREEN]` ```
> smflow build lab-01.smflow --target linux-x64 --emit-only
> ```
> `ls generated/` — five files.

**[VO]** Emit-only. Generate the C++, don't invoke the cross-compiler. Five files.

> `[SCREEN]` Full-frame `application.cpp`, 20pt+.

**[VO]** application.cpp. This is your logic.

**[BEAT — let them read it]**

**[VO]** Two lines. There are your names — StartButton, Motor. A reviewer looking at this in a pull
request doesn't need the graph open to know what it does.

**[VO]** And notice what isn't here. Where did the NOT node go?

**[BEAT]**

> `[ON-SCREEN TEXT]` → `!`

**[VO]** It became an exclamation mark. Which is what an exclamation mark is for. The node was
notation for the program. It was never a thing *in* the program.

### The grep

> `[SCREEN]` ```
> grep -rnE '\b(Node|Graph|ExecuteNode|Runtime|Interpreter|ScriptEngine)\b' \
>      --include='*.cpp' --include='*.h' generated/
> ```
> Empty result. Hold it on screen.

**[VO]** Whole generated directory. Node. Graph. ExecuteNode. Runtime. Interpreter. ScriptEngine.

**[BEAT]**

**[VO]** Nothing. There's no node registry, no dispatch loop, no visitor pattern, no interpreter.
The controller never finds out a graph existed.

**[VO]** And there's no SMFlow on the target either. No .NET, no Node, no Python, no runtime
library of ours. If this company disappeared tomorrow, that C++ still compiles and you can still
maintain it by hand.

> `[ON-SCREEN TEXT]` No runtime on the controller. None.

### The scan loop

> `[SCREEN]` `main.cpp`, scrolled to the while loop. Full frame.

**[VO]** Here's main. Read inputs. Run the task. Write outputs. Sleep until the next deadline.

**[VO]** If you've written a PLC scan loop or a bare-metal superloop, you've written this function.
Lab 2 takes it apart properly. For now I just want you to notice that it's a loop *you could have
written* — and that it explains itself.

> `[SCREEN]` Highlight the `SleepUntil` comment.

**[VO]** That comment is explaining why the sleep is against an absolute deadline instead of a
relative one — because a relative sleep adds the scan time to every tick and drifts. That's the
kind of thing a good firmware engineer writes down. Our code generator writes it down.

### Determinism

> `[SCREEN]` ```
> smflow build ... --out build-a
> smflow build ... --out build-b
> diff -r build-a build-b
> ```
> No output.

**[VO]** Build it twice. Diff it. Nothing.

**[VO]** No timestamps, no generated IDs, no dictionary ordering leaking into the output. Same
project in, byte-identical C++ out, every time.

**[VO]** That's not a party trick. That's what makes the generated code reviewable. A diff in your
repo shows what you changed in the graph — and nothing else.

> `[ON-SCREEN TEXT]` Same graph in → byte-identical C++ out

---

## Break it (14:00 – 15:45)

> `[SCREEN]` Delete the wire between NOT and Motor. Validate.
> ```
> error SMF0005: Required input 'value' on Digital Output node 'motor' is not connected. [node motor]
> ```

**[VO]** Let's break it. Delete that wire.

**[BEAT]**

**[VO]** Error. And three things here are deliberate.

**[VO]** One — it did *not* generate code. It didn't give me a Motor that holds its last value, or
defaults to false, or warns and carries on. It refused. The gate is before code generation, not
after.

**[VO]** Two — it names the node. In the editor that highlights it on the canvas.

**[VO]** Three — SMF0005. Stable error code. Greppable. Which you'll appreciate the first time you
triage a CI failure at two in the morning.

> `[SCREEN]` Reconnect. Validate. Valid.

---

## What just happened (15:45 – 17:30)

> `[SCREEN]` Simple diagram, built up one stage at a time:
> ```
> .smflow  →  validate  →  typed IR  →  lowering  →  C++  →  native binary
> ```

**[VO]** Here's the model I want you to leave with.

**[VO]** SMFlow is a compiler. Not a runtime, not a scripting host, not a visual shell over a
library. The graph is source code in the completely ordinary sense — it gets parsed, type-checked,
lowered to an intermediate representation, and translated to a target language. Ahead of time.

**[VO]** Three consequences you'll feel for the rest of this series.

**[VO]** The generated code goes in your repo and through your review process, and determinism is
what makes that diff mean something.

**[VO]** An invalid graph is not runnable. There's no "it built, let's see what happens on the
bench."

**[VO]** And the editor is optional. Everything I did today, I could have done from the CLI — and I
showed you both. Your build server never installs the editor.

**[BEAT]**

**[VO]** The cost is the one you already paid: you need a C++ toolchain for your target, even to
simulate. SMFlow trades a bit of setup friction for the complete absence of an interpreter. For
industrial control, I'll take that trade every time.

---

## Next (17:30 – 18:00)

**[VO]** Next lab, we open up that scan loop. Inputs sampled once at the top, outputs written once
at the bottom, and execution order that comes from the graph and not from where you dropped the
nodes. If you've got PLC instincts, most of them are about to transfer — and one of them isn't.

> `[ON-SCREEN TEXT]` Lab 2 — The scan cycle
> Written lab + project files: [link]

---

# Shorts

## Short 1 — "The grep" (45 s)

**Claim:** There is no graph in the generated code.

> `[0:00–0:06, shot for vertical]` Full-frame generated C++, two lines of logic.

**[VO]** Visual programming tools have a reputation for generating unreviewable code. Let's test
it.

> `[0:06–0:16]` Cut to the three-node graph. Then back.

**[VO]** Three nodes in. Two lines of C++ out. Your names, right there.

> `[0:16–0:32]` The grep, typed live. Empty result held for three full seconds.

**[VO]** Node, Graph, ExecuteNode, Runtime, Interpreter, ScriptEngine — across the entire generated
output.

**[BEAT]**

**[VO]** Nothing. No dispatch loop. No interpreter. The controller never learns a graph existed.

> `[0:32–0:45]`

**[VO]** That's SMFlow. It's a compiler, not a runtime. Full lab in the description.

---

## Short 2 — "Build it twice" (35 s)

**Claim:** Generated code is byte-identical build to build, which is what makes it reviewable.

> `[0:00–0:08, vertical]` Split screen, two terminal builds running.

**[VO]** Here's a question nobody asks a code generator until it burns them. Build the same project
twice — do you get the same file?

> `[0:08–0:22]` `diff -r build-a build-b`. No output. Hold.

**[VO]** Diff. Nothing. No timestamps, no generated IDs, no hash ordering sneaking into the output.

> `[0:22–0:35]` Cut to a GitHub diff view of a real graph change: small, legible.

**[VO]** Which means when you change one node, your pull request shows one change. Generated code
you can actually review.

---

## Short 3 — "It refuses" (40 s)

**Claim:** An invalid graph does not build. At all.

> `[0:00–0:07, vertical]` Cursor deletes a wire in the editor. Clean, deliberate.

**[VO]** Watch what happens when I disconnect this output.

> `[0:07–0:20]` Validate. The SMF0005 error, full-frame.

**[VO]** It refused. Not a warning. Not a default value. Not "best effort, check it on the bench."
No code at all.

> `[0:20–0:40]` Highlight `[node motor]`, then cut to the editor with that node highlighted on the
> canvas.

**[VO]** It names the node — that selects it on the canvas. And it has a stable error code you can
grep in CI.

**[VO]** Validation runs before code generation. Every time. That's not a setting.
