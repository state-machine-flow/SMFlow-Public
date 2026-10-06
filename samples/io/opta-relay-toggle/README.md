# opta-relay-toggle — alternating relay pairs at 0.5 Hz on an Arduino Opta

A minimal hardware sample for the Arduino Opta that toggles its four electromechanical relays
at **0.5 Hz** (1.0 s ON, 1.0 s OFF, 2.0 s total cycle period) in complementary pairs:

- When **Relays 1 and 3** are **ON**, **Relays 2 and 4** are **OFF**.
- When **Relays 1 and 3** are **OFF**, **Relays 2 and 4** are **ON**.

```
Run (true) ──▶ IN ┌───────────────┐
                  │     Blink     │ Q ──┬─────────────────────▶ Relay1 (RELAY1, OUTPUT 1)
                  │ 1000ms/1000ms │     ├─────────────────────▶ Relay3 (RELAY3, OUTPUT 3)
                  └───────────────┘     │
                                        └──▶ ┌─────┐
                                             │ NOT │ ──┬──────▶ Relay2 (RELAY2, OUTPUT 2)
                                             └─────┘   └──────▶ Relay4 (RELAY4, OUTPUT 4)
```

## Relays & Front-Panel Status LEDs

Each relay terminal is bound in `opta-relay-toggle.iomap`:

| Logical Resource | Physical Resource | Screw Terminal | Status LED | Phase A (0.0–1.0 s) | Phase B (1.0–2.0 s) |
|---|---|---|---|---|---|
| `Relay1` | `RELAY1` | OUTPUT 1 | `LED_D0` | **ON** | OFF |
| `Relay2` | `RELAY2` | OUTPUT 2 | `LED_D1` | OFF | **ON** |
| `Relay3` | `RELAY3` | OUTPUT 3 | `LED_D2` | **ON** | OFF |
| `Relay4` | `RELAY4` | OUTPUT 4 | `LED_D3` | OFF | **ON** |

On the Arduino Opta front face, each relay output has a dedicated status LED (`LED_D0` to `LED_D3`).
SMFlow's Opta target backend automatically mirrors each relay's commanded state to its matching status
LED.

When powered purely over USB-C on a bench, the front-panel LEDs alternate immediately to confirm
firmware operation. When external 12–24 VDC power is supplied to the Opta's supply terminals, the internal
mechanical relay coils will energize and click in sync with the LEDs.

## Running and testing

### From the editor

Open `opta-relay-toggle.smflow`, verify the target selector reads `opta`, and press:
- **F5** to simulate
- **F6** to build native firmware
- **F7** to deploy directly to an attached Opta

### From the CLI

Validate and run the deterministic test suite:

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
    const bool t0 = LoadShared_Run();
    const uint64_t t1 = Now();
    const bool t2 = state.s1_running;
    const uint64_t t3 = state.s1_started;
    const uint64_t t5 = t0 ? (t2 ? t3 : t1) : 0ull;
    const uint64_t t8 = (t1 - t5) % (1000ull + 1000ull);
    const bool t10 = t0 && t8 < 1000ull;

    state.s1_running = t0;
    state.s1_started = t5;
    const bool t12 = !t10;

    io.Relay1 = t10;
    io.Relay2 = t12;
    io.Relay3 = t10;
    io.Relay4 = t12;
}
```
