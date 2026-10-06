# opta-relay-toggle — alternating relay pairs at 0.5 Hz on an Arduino Opta

A hardware sample for the Arduino Opta that blinks its four electromechanical relays at **0.5 Hz**
(1.0 s ON, 1.0 s OFF, 2.0 s total cycle period) in complementary pairs, with a **user-button
pause/resume that freezes the relays in their current state**:

- When **Relays 1 and 3** are **ON**, **Relays 2 and 4** are **OFF**.
- When **Relays 1 and 3** are **OFF**, **Relays 2 and 4** are **ON**.
- Press the **user button** to pause. The relays **hold whatever pattern they were showing**.
- Press again to resume — blinking continues from exactly where it paused (a true pause, not a
  restart).

```
Enable (true) ─▶ IN ┌───────────────┐
                    │     Blink     │ Q ──┬─────────────────────▶ Relay1, Relay3
  Input1 ─▶ ┌────────┐ 1000/1000 ms │     │
 (button)   │ Toggle │ Q ─▶ pause   │     └──▶ ┌─────┐
            └────────┘ └─────────────┘         │ NOT │ ─▶ Relay2, Relay4
                                               └─────┘
```

### How pause works

The button drives a `toggle`, whose output feeds Blink's **`pause`** input. While `pause` is true,
Blink freezes **both its output and its phase**: `Q` holds its current level, and the internal timer
stops advancing. The relays therefore hold exactly the pattern they were showing, and pressing again
resumes the same half-cycle instead of restarting it.

This is why pausing does **not** snap the relays to a fixed 2 & 4. Earlier the only way to "stop" a
blinker was to drop its `IN` (enable) input, which *clears* `Q` to false — and the `NOT` feeding
Relays 2 & 4 then forced those two ON every time. The `pause` input holds the state instead of
clearing it, so there is no sample-and-hold to build by hand.

`Enable` is a variable held `true` that satisfies Blink's required `IN` input so the blinker runs;
nothing ever writes it.

## Relays & Front-Panel Status LEDs

Each relay terminal is bound in `opta-relay-toggle.iomap`; `Input1` binds to the Opta user button,
configured with a pull-up (it is active-low: pressed reads LOW).

| Logical Resource | Physical Resource | Screw Terminal | Status LED | Phase A (0.0–1.0 s) | Phase B (1.0–2.0 s) |
|---|---|---|---|---|---|
| `Relay1` | `RELAY1` | OUTPUT 1 | `LED_D0` | **ON** | OFF |
| `Relay2` | `RELAY2` | OUTPUT 2 | `LED_D1` | OFF | **ON** |
| `Relay3` | `RELAY3` | OUTPUT 3 | `LED_D2` | **ON** | OFF |
| `Relay4` | `RELAY4` | OUTPUT 4 | `LED_D3` | OFF | **ON** |
| `Input1` | `BTN_USER` | User Button | — | pause / resume | pause / resume |

On the Arduino Opta front face, each relay output has a dedicated status LED (`LED_D0` to `LED_D3`).
SMFlow's Opta target backend automatically mirrors each relay's commanded state to its matching
status LED.

When powered purely over USB-C on a bench, the front-panel LEDs alternate immediately to confirm
firmware operation. When external 12–24 VDC power is supplied to the Opta's supply terminals, the
internal mechanical relay coils will energize and click in sync with the LEDs.

## Build it in two stages (training walkthrough)

This sample ships in two files so the pause button can be added as a live edit:

1. **`opta-relay-toggle.start.smflow`** — the always-running version: `Enable → Blink → relays`,
   with Blink's `pause` input left open (so it never pauses).
2. **`opta-relay-toggle.smflow`** — the finished version with the user button.

Going from (1) to (2) on camera is **purely additive** — nothing is rewired or deleted:

- **Add** a `digital-input` named `Input1` and a `toggle` node.
- **Wire** `Input1.value → toggle.CLK`, then `toggle.Q → Blink.pause`.

Because `pause` is an optional input, the always-running version needs no placeholder for it; you
simply connect the button when you are ready. The toggle starts `false` (running); each press flips
Blink's `pause`.

## Running and testing

### From the editor

Open `opta-relay-toggle.smflow`, verify the target selector reads `opta`, and press:
- **F5** to simulate
- **F6** to build native firmware
- **F7** to deploy directly to an attached Opta

### From the CLI

Validate and run the deterministic test suite (covers the blink timing, the pause freeze, and that
resuming continues mid-cycle):

```bash
smflow validate samples/io/opta-relay-toggle/opta-relay-toggle.smflow
smflow test     samples/io/opta-relay-toggle/opta-relay-toggle.smflow
```

Build the Arduino Opta firmware sketch:

```bash
smflow build samples/io/opta-relay-toggle/opta-relay-toggle.smflow --target opta
```

Deploy to a USB-connected Opta:

```bash
smflow controllers
smflow deploy samples/io/opta-relay-toggle/opta-relay-toggle.smflow --target opta
```

Flashing requires `arduino-cli` on PATH and the Opta Mbed core installed:

```bash
arduino-cli core install arduino:mbed_opta
```

## What it generates

The entire scan loop body from `application.cpp`:

```cpp
void MainTask(IO& io, State& state)
{
    const bool t0 = LoadShared_Enable();
    const bool input1 = io.Input1;
    const bool t2 = state.s1_latched;
    const bool t3 = state.s1_previous;
    const bool t8 = false ? false : input1 && !t3 ? !t2 : t2;   // toggle: the pause flag

    state.s1_latched = t8;
    state.s1_previous = input1;
    const uint64_t t9 = Now();
    const bool t10 = state.s2_running;
    const uint64_t t11 = state.s2_started;
    const uint64_t t12 = state.s2_last;
    const uint64_t t14 = t0 ? (t10 ? t11 : t9) : 0ull;
    const uint64_t t19 = t0 && t8 && t10 ? t14 + (t9 - t12) : t14;  // paused: carry start forward
    const uint64_t t22 = (t9 - t19) % (1000ull + 1000ull);
    const bool t24 = t0 && t22 < 1000ull;                          // Q (high phase)

    state.s2_running = t0;
    state.s2_started = t19;
    state.s2_last = t9;
    const bool t26 = !t24;

    io.Relay1 = t24;
    io.Relay2 = t26;
    io.Relay3 = t24;
    io.Relay4 = t26;
}
```

The pause lives in `t19`: while the pause flag `t8` is set, the blinker's start time is carried
forward by the time elapsed since the last scan (`t9 - t12`), so its phase stands still and `Q`
holds.
