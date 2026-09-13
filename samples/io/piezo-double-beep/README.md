# Piezo double-beep — a gated tone on an Arduino Mega 2560

Two short beeps at power-up, then silence. The kind of confirmation chime a panel makes when it
comes up healthy.

```
                 ┌─► TON 300ms ─► NOT ──┐
Always (true) ───┤                      ├─► AND ─► cond ┐
                 └─► Blink 100/100 ─────┘               │
                                                        ▼
                          AlarmHz (2700) ─► whenTrue  ┌────────┐
                          Silent  (0)    ─► whenFalse │ Select │─► Buzzer (tone-output, D6)
                                                      └────────┘

Always (true) ─────────► Blink 500/500 ───────────────────────► Heartbeat (D13, onboard LED)
```

Eleven nodes, which builds on the free tier.

## Wiring

| | |
|---|---|
| Board | Arduino Mega 2560 R3 (`atmega2560-mega`) |
| Buzzer | **D6** — a passive piezo disc, other leg to GND |
| Heartbeat | **D13** — the onboard LED. Nothing to wire |
| Supply | 5 V |

A piezo is the only part you need. **It must be a *passive* piezo, not an active buzzer** — an active
buzzer contains its own oscillator, sounds at one fixed pitch, and is a `digital-output`. The two
look nearly identical and nothing in the program can tell them apart.

**2700 Hz is not arbitrary.** A piezo disc has a resonant frequency, typically 2–4 kHz, where it is
dramatically louder. The same disc at 440 Hz can be nearly inaudible.

## How the gate works

`tone-output` takes a frequency, and a frequency is a number — so making a tone start and stop means
**choosing between two numbers on a condition**. That is what `select` is for, and it is the only
node that turns a decision into a value; everything else in the logic family produces a bool.

The two-pulse window is ordinary boolean logic:

| | `Blink` | `TON.Q` | `NOT` | `AND` → tone |
|---|---|---|---|---|
| 0–100 ms | true | false | true | **2700 Hz** |
| 100–200 ms | false | false | true | silent |
| 200–300 ms | true | false | true | **2700 Hz** |
| after 300 ms | alternating | true | false | silent, forever |

The blink keeps oscillating after 300 ms — the `TON` is what makes it a *double* beep rather than an
endless one. Change `TON`'s preset to 500 ms and you get three beeps; the pattern is the timer, not
the node count.

`select` lowers to a plain C++ ternary — an expression, not a branch — so the task stays one
straight-line sequence and the cost of a scan does not depend on the data:

```cpp
io.Buzzer = !(t0 && (t0 ? t1 - t5 : 0ull) >= 300ull) && (t0 && t17 < 100ull) ? t22 : t23;
```

Both arms are evaluated regardless of the condition. That is deliberate: a scan that took longer on
one branch than the other would make timing depend on data, which the determinism model forbids.

## The heartbeat matters

The LED blinks at 1 Hz forever, and it is what makes this diagnostic rather than pass/fail:

| LED | Sound | Means |
|---|---|---|
| Blinking | Two beeps at power-up | Working |
| Blinking | Silent | The program is running — it is the piezo, the D6 wiring, or an active buzzer where a passive one is needed |
| Dark | Silent | Did not flash, or did not boot |

Without it, silence cannot distinguish a dead piezo from a board that never started.

Press **reset** to hear the beeps again.

## Building

```bash
smflow validate samples/io/piezo-double-beep/project.smflow
smflow build    samples/io/piezo-double-beep/project.smflow --target atmega2560-mega
smflow build    samples/io/piezo-double-beep/project.smflow --target simulator
```

The Mega build compiles with `arduino-cli` to roughly 6.1 KB of flash and 144 bytes of RAM.

In the simulator, watch `Buzzer` step 2700 → 0 → 2700 → 0 as you `advance 100` four times.

## Timers

`tone()` takes **Timer2** on an AVR, which also drives PWM on D9 and D10 — bind a `pwm-output` to
either while a tone is claimed and the build warns, naming both. Nothing here contends: D6 carries
the tone as an ordinary digital pin, and this project declares no PWM.

Arduino sounds **one tone at a time**, so a second `tone-output` node anywhere in a program is a
compile error rather than a silently dead node.

## Caveats

- **A 100 ms beep is short by design.** Lengthen both the `Blink` times and the `TON` preset together
  — the preset must equal `high + low + high` or you will clip the second beep or start a third.
- **Below about 31 Hz the AVR tone path cannot produce a waveform.** Not a concern here, but it is
  why a frequency computed at run time is clamped at the backend rather than rejected at compile
  time.
- **The Opta refuses this project**, correctly: its outputs are relays and it declares no tone timer.
  Retargeting fails loudly rather than quietly doing nothing.
