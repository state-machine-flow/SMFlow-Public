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
| `serial-debug` | atmega328-uno, linux-x64, simulator | Printing a labelled, formatted value to a serial console |
| `single-counter` | simulator, opta, rp2040-pico, any | Canonical IEC 61131-3 counter block with edge detection, preset, and reset |

### logic/ — combinational and latching behavior
| Sample | Targets | Shows |
|---|---|---|
| `motor-interlock` | simulator, any | Safety interlock, multi-input logic |

### timing/ — delays, periods, and edges
| Sample | Targets | Shows |
|---|---|---|
| `start-delay` | simulator, any | On-delay inside a periodic task |
| `stopwatch` | simulator, any | Toggle latch, accumulating an int32 counter per scan |
| `step-sequencer` | simulator, opta, rp2040-pico, any | Multi-stage process control using cascaded on-delay timers and interlocked gates |

### io/ — real pins on real boards
| Sample | Targets | Shows |
|---|---|---|
| `pico-latch` | rp2040-pico | A two-state latch, `.iomap` pin binding |
| `pico-interlock` | rp2040-pico | The interlock running on hardware |
| `opta-interlock` | opta | The interlock on an Arduino Opta |
| `opta-relay-toggle` | opta, simulator | Alternating relay pairs at 0.5 Hz (1 & 3 vs 2 & 4) |
| `opta-2-bit-counter` | opta, simulator, linux-x64 | 4-relay sequential stepper using user button and a 2-bit ripple counter |
| `pwm-piezo` | atmega2560-mega, simulator | A PWM duty cycle and a piezo tone, and the timers they claim |
| `piezo-double-beep` | atmega2560-mega, simulator | Gating a tone with `select`; a piezo and nothing else to wire |

### peripherals/ — peripherals over I²C and SPI
| Sample | Targets | Shows |
|---|---|---|
| `ssd1306-text` | rp2040-pico, esp32-s3, simulator | Text and counters on an I²C OLED |
| `ws2812-indicator` | rp2040-pico, esp32-s3, simulator | Addressable RGB LED strip status indicator over SPI MOSI |

### applications/ — end-to-end, closer to a real product
| Sample | Targets | Shows |
|---|---|---|
| `lora-press-counter` | rp2040-pico, esp32-s3 | Binary LoRa packets with a payload schema |
| `modbus-analog` | atmega2560-mega | Four analog channels served as Modbus TCP input registers, and a fallback when the client goes away |
| `modbus-diagnostic` | atmega2560-mega | The same server with its status counters on a 20x4 LCD — a commissioning tool for when a client gets nothing back |

### reference/ — industry reference architectures and retrofits
| Sample | Targets | Shows |
|---|---|---|
| `automotive/alternator-regulator` | rp2040-pico, simulator | Standalone ECU replacement for 2020 GM Duramax alternator (84143541 / 23298275) with 128 Hz PWM RVC regulation, soft-start, thermal derating, and overvoltage latching |
| `automotive/cooling-fan-controller` | rp2040-pico, simulator | Standalone dual electric cooling fan controller (EF-ECU) with staged PWM, 5°C hysteresis, A/C override, highway ram-air lockout, after-run rundown cooling, and fail-safe diagnostics |
| `automotive/seat-climate-controller` | rp2040-pico, simulator | Retrofit heated and cooled seat controller (CCSM) with 3-level thermostatic regulation, PWM fan control, soft-start, open/short sensor detection, and ignition rundown timeout |
| `automotive/wiper-controller` | rp2040-pico, simulator | Standalone windshield wiper control module (WCM) with multi-speed interlocked wiping, immediate first-wipe intermittent timing, washer drip cycles, auto-park detection, ignition-off rundown, and dual watchdog stall timeouts |
| `automotive/power-window-controller` | rp2040-pico, simulator | Standalone power window controller module (WCM) with momentary/express travel, FMVSS 118 anti-pinch reversal, end-stop stall cutoff, and 30s Retained Accessory Power with door cancel |

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
