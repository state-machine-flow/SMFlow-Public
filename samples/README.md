# SMFlow samples

Each sample is a complete project folder. Open the `project.smflow` in the editor and press **F5**
to simulate or **F6** to build — that is all a sample needs.

The `smflow` CLI, installed alongside the editor, does the same from a script, and is the only way to
run the `.smtest` suites some samples ship. It is not on your `PATH` by default; see
[the CLI guide](../docs/guide/cli.md).

```
smflow validate samples/basics/not-gate/project.smflow
smflow simulate samples/basics/not-gate/project.smflow
smflow build    samples/basics/not-gate/project.smflow --target linux-x64
```

## Catalog

### basics/ — one idea each, nothing extra
| Sample | Targets | Shows |
|---|---|---|
| `not-gate` | simulator, any | The minimal complete program |

### logic/ — combinational and latching behavior
| Sample | Targets | Shows |
|---|---|---|
| `motor-interlock` | simulator, any | Safety interlock, multi-input logic |

### timing/ — delays, periods, and edges
| Sample | Targets | Shows |
|---|---|---|
| `start-delay` | simulator, any | On-delay inside a periodic task |

### io/ — real pins on real boards
| Sample | Targets | Shows |
|---|---|---|
| `pico-latch` | rp2040-pico | A two-state latch, `.iomap` pin binding |
| `pico-interlock` | rp2040-pico | The interlock running on hardware |
| `opta-interlock` | opta | The interlock on an Arduino Opta |
| `pwm-piezo` | atmega2560-mega, simulator | A PWM duty cycle and a piezo tone, and the timers they claim |
| `piezo-double-beep` | atmega2560-mega, simulator | Gating a tone with `select`; a piezo and nothing else to wire |

### devices/ — peripherals over I²C and SPI
| Sample | Targets | Shows |
|---|---|---|
| `ssd1306-text` | rp2040-pico, esp32-s3, simulator | Text and counters on an I²C OLED |

### applications/ — end-to-end, closer to a real product
| Sample | Targets | Shows |
|---|---|---|
| `lora-press-counter` | rp2040-pico, esp32-s3 | Binary LoRa packets with a payload schema |

## What a sample folder contains

```
sample-name/
  README.md         what it does, wiring, how to run it
  project.smflow    the flow itself — this is the source
  project.iomap     pin/terminal bindings, when the sample targets hardware
  sample.smtest     graph-level tests, where the behavior is worth asserting
```

Generated C++ and build output are **not** checked in — they are reproducible from the flow.

## Contributing a sample

Good samples teach exactly one thing, are small enough to read on one screen, and validate cleanly
against the current release. See [CONTRIBUTING.md](../CONTRIBUTING.md#contributing-a-sample).
