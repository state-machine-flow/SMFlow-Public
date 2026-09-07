# pico-latch — a two-state machine on a Raspberry Pi Pico

The smallest program that is genuinely a state machine rather than a function of its inputs: a
start/stop latch. It has two states, **Stopped** and **Running**, and which one it is in depends on
what happened earlier, not on what the inputs read this scan.

```
StartButton ──▶ S ┌───────────┐
                  │ Set/Reset │ Q ──▶ RunLamp
StopButton  ──▶ R └───────────┘
```

Set wins if both are pressed in the same scan, so the lamp cannot be left in an undefined state by a
simultaneous press.

## Wiring

| Logical | Pin | What |
|---|---|---|
| `StartButton` | `GP16` | momentary to 3.3 V |
| `StopButton` | `GP15` | momentary to 3.3 V |
| `RunLamp` | `GP25` | the Pico's **on-board LED** — nothing to wire |

`RunLamp` is on GP25 on purpose: the board's own LED is the output, so a freshly flashed Pico shows
the state machine working before any buttons are attached. With nothing connected to GP16 and GP15
those inputs float, so add a pull-down to each once you want deterministic buttons.

Every pin is 3.3 V logic and **not** 5 V tolerant.

## Deploying it

From the editor: open `project.smflow`, check the target strip reads `rp2040-pico`, choose the board
in the Device box, and press **F7** (Build ▸ Deploy to Device).

From the CLI:

```
smflow devices
smflow deploy examples/pico-latch/project.smflow
```

A Pico that has never been programmed has no serial port. Hold **BOOTSEL** while plugging it in and
it appears as a drive called `RPI-RP2`, which takes the `.uf2` by file copy. A board already running
firmware appears as a serial port instead and is flashed with `arduino-cli`. Both are handled; the
drive is tried first because it is the one that always works.

Requires `arduino-cli` on PATH and the RP2040 core:

```
arduino-cli core install arduino:mbed_rp2040
```

## What it generates

The whole scan body, from `application.cpp`:

```cpp
void MainTask(IO& io, State& state)
{
    const bool startButton = io.StartButton;
    const bool stopButton = io.StopButton;
    const bool t2 = state.s1_latched;
    const bool t5 = startButton || t2 && !stopButton;

    state.s1_latched = t5;
    io.RunLamp = t5;
}
```

`Q = S || (Q && !R)` — the latch, as ordinary C++. The state lives in a named field of a plain
struct, not in a runtime, and nothing on the board interprets a graph.
