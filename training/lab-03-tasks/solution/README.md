# Lab 3 — "On your own" solution

A 500 ms / 500 ms heartbeat in the `Report` task.

Three nodes added: a `variable-read` of a new `TrueConst` variable (the constant idiom again —
`blink` needs an enable on its `IN` port), the `blink` itself, and a `Heartbeat` digital output.

```
smflow validate lab-03-solution.smflow
smflow build    lab-03-solution.smflow --target linux-x64 --emit-only
```

## The answers

### 1. Where does the blink's state live?

In a `State` struct, declared in `application.h` and passed to the task by reference:

```cpp
struct State
{
    bool s1_running;
    uint64_t s1_started;
};
```

Note the signature change. `ReportTask` was `void ReportTask(IO& io)`; it is now:

```cpp
void ReportTask(IO& io, State& state)
```

A task that carries no state across scans does not get a `State&` parameter at all. The moment one
node needs retained state, the task's signature changes to carry it. Nothing is allocated, nothing
is global, and nothing is hidden — the state is a plain struct, visible in the header.

The `s1_` prefix is the state slot's index, assigned in execution order. That ordering is
deterministic, which is why the generated code is byte-identical build to build even though the
names are synthesized.

### 2. What is Report's state size now?

```
  Task        Period      Nodes   Ops   State Size
  Startup     init        2       2     0 B
  Control     10 ms       5       5     0 B
  Report      250 ms      5       17    9 B
  Total: 3 task(s), 12 node(s), 24 operation(s), 9 B state
```

**9 bytes** — one `bool` plus one `uint64_t`. Also worth noticing: `Report` went from 2 operations
to 17. A `blink` is not a cheap node, and the report tells you so before you go looking for the
cost on a part with 2 KB of RAM.

### 3. What if the blink were 100 ms in a 250 ms task?

It would alias, and the output would be visibly wrong.

Look at how `blink` is actually implemented:

```cpp
const uint64_t t2 = Now();
...
const uint64_t t9 = (t2 - t6) % (500ull + 500ull);

io.Heartbeat = t1 && t9 < 500ull;
```

The timer reads **the clock**, not a scan counter. It computes where it is in its cycle from
elapsed milliseconds. So the node's notion of time is continuous and correct — but it is only
*sampled* when its task runs.

At 500/500 in a 250 ms task you sample a 1000 ms waveform every 250 ms: four samples per cycle,
and the output looks right.

At 100/100 you are sampling a 200 ms waveform every 250 ms. The sample rate is below the Nyquist
rate for that signal, so what reaches the pin is an aliased pattern — slow, irregular, and nothing
like 100 ms. It will also look *stable*, which is worse, because it does not read as a bug.

The general rule: **a timing node cannot be faster than the task that samples it.** Keep the
period comfortably shorter than the shortest interval the node needs to resolve. Lab 6 comes back
to this with `ton` and `tof`, where the same trap has sharper consequences.
