# Lab 5 — "On your own" solution

A single-button station: `RunButton` toggles the motor, `StopButton` forces it off.

`set-reset` is replaced by `toggle`, and `StopButton` moves to the toggle's `R`. The counter and
the falling-edge pulse are unchanged — they just read the toggle's `Q` instead of the latch's.

```
smflow validate lab-05-solution.smflow
smflow build    lab-05-solution.smflow --target linux-x64 --emit-only
```

```cpp
void MainTask(IO& io, State& state)
{
    const bool runButton = io.RunButton;
    const bool stopButton = io.StopButton;
    const bool t2 = state.s1_latched;
    const bool t3 = state.s1_previous;
    const bool t8 = stopButton ? false : runButton && !t3 ? !t2 : t2;

    state.s1_latched = t8;
    state.s1_previous = runButton;
    ...
}
```

## The answers

### 1. What is `toggle`'s second state slot for?

```cpp
struct State
{
    bool s1_latched;    // the output — am I on?
    bool s1_previous;   // last scan's CLK — has the button just been pressed?
    ...
};
```

`s1_latched` is the toggle's output. `s1_previous` is **its own edge detector on `CLK`**.

A toggle has to flip on the *press*, not while the button is held. Held down for 300 scans with no
edge detection, it would flip 300 times and land somewhere arbitrary. So it remembers last scan's
`CLK` and acts only on the transition:

```cpp
runButton && !t3 ? !t2 : t2
```

Press detected → invert. Otherwise → hold.

`set-reset` needs no such thing because it is **level-driven by construction**. `S` high means be
on; `S` high again next scan still means be on. Re-asserting a level is idempotent, so there is
nothing an edge would tell it that the level does not.

This is the same mechanism you found inside `counter` in the main lab, and it is why wiring a
level into `CU` or `CLK` is correct rather than a bug.

### 2. Is `toggle`'s reset dominant?

**Dominant.** Straight from the expression:

```cpp
stopButton ? false : (runButton && !t3 ? !t2 : t2)
```

`stopButton` is the outermost condition. If it is true, the result is `false` and nothing else
is even evaluated. Press the run button and hold stop, and the motor stays off.

Note this is the *opposite* precedence to `set-reset`, which is Set-dominant
(`startButton || ...`). Two state nodes, two different answers, and in both cases you read it off
one line of generated C++ rather than trusting a table.

Dominant reset is the behavior you want here: a stop that can be overridden by mashing the run
button is not a stop. That seems too obvious to check — which is exactly why it is worth checking,
and the generated expression is where you check it.

### 3. Where did the extra byte go?

```
  Main        10 ms       9       29    8 B
```

7 bytes → 8. The extra byte is `s1_previous`, the toggle's edge-detector bool.

The counter and falling-edge slots are unchanged. `set-reset` carried one bool; `toggle` carries
two. One button instead of two cost you one byte of RAM and four extra operations — which is a
genuinely reasonable trade, and the build report let you make it with a number instead of a guess.
