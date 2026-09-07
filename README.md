# SMFlow

**Visual programming that compiles to native C++ — no runtime on the device.**

SMFlow is a desktop environment for building deterministic industrial and embedded control programs
as a node-and-wire graph. The graph *is* the source code. It is compiled ahead of time into ordinary,
readable C++ and then into a native binary for your target.

There is no interpreter, no scripting engine, and no SMFlow runtime on the device. Your Pico, ESP32,
Opta, or Linux box runs plain compiled code — nothing else has to be installed.

- Website: **[smflow.co](https://smflow.co)**
- Downloads: **[smflow.co/download](https://smflow.co/download)** and [Releases](../../releases)
- Pricing: **[smflow.co/pricing](https://smflow.co/pricing)**

---

## What's in this repository

This is the **public** companion repo for SMFlow. The product source is closed and lives elsewhere.
Here you'll find:

| Folder | Contents |
|---|---|
| [`docs/`](docs/) | User documentation — installation, first flow, node reference, target guides |
| [`samples/`](samples/) | Ready-to-open example flows, from a NOT gate to LoRa telemetry |
| [`releases/`](releases/) | Release notes and the changelog |
| [Releases](../../releases) | Installer downloads for Windows, macOS, and Linux |
| [Issues](../../issues) | Bug reports and feature requests |
| [Discussions](../../discussions) | Questions, showcase, and help |

## Quick start

1. Download the installer for your platform from [Releases](../../releases).
2. Install and launch SMFlow.
3. Open `samples/basics/not-gate` — the smallest complete program: `Motor = !StartButton`.
4. Press **F5** to run it in the simulator, or pick a hardware target and press **F6** to build.

Everything above happens in the editor. The `smflow` CLI installs alongside it for scripting, graph
tests, and CI — see [docs/guide/cli.md](docs/guide/cli.md) — but you never need it to use SMFlow.

Full walkthrough: [docs/getting-started/first-flow.md](docs/getting-started/first-flow.md)

## Supported targets

| Target | ID | Notes |
|---|---|---|
| Desktop simulator | `simulator` | Run and step a flow with no hardware |
| Linux x64 | `linux-x64` | Static native binary |
| Linux ARM64 | `linux-arm64` | Raspberry Pi and similar SBCs |
| Arduino Opta | `opta` | Industrial PLC form factor |
| Raspberry Pi Pico | `rp2040-pico` | RP2040 |
| Arduino Nano RP2040 Connect | `rp2040-nano-connect` | RP2040 |
| ESP32-S3 | `esp32-s3` | Wi-Fi / BLE class MCU |
| Arduino Nano (ATmega328) | `atmega328-nano` | 8-bit AVR |
| Portable C++ | `portable` | Vendor-neutral C++17 you integrate yourself |

Run `smflow targets` to see what your installed build supports.
Hardware details: [docs/targets/](docs/targets/)

## Samples

Each sample is a complete project folder you can open directly in the editor.

| Sample | Shows |
|---|---|
| [`basics/not-gate`](samples/basics/not-gate) | The minimal flow — one input, one gate, one output |
| [`logic/motor-interlock`](samples/logic/motor-interlock) | Safety interlock with combinational logic |
| [`timing/start-delay`](samples/timing/start-delay) | On-delay timing in a periodic task |
| [`io/pico-latch`](samples/io/pico-latch) | A two-state latch on a Raspberry Pi Pico |
| [`devices/ssd1306-text`](samples/devices/ssd1306-text) | Text and telemetry on an I²C OLED |
| [`applications/lora-press-counter`](samples/applications/lora-press-counter) | Binary LoRa packets from a button counter |

See [samples/README.md](samples/README.md) for the full catalog and contribution rules.

## Reporting a problem

Open an [issue](../../issues/new/choose). Please include your SMFlow version (**Help → About**),
your OS, your target, and — where you can share it — the `project.smflow` file that reproduces it.

Security reports should go to **security@smflow.co**, not to a public issue.
See [SECURITY.md](SECURITY.md).

## Licensing

SMFlow itself is commercial software; see [smflow.co/pricing](https://smflow.co/pricing).

The contents of *this* repository — documentation and sample flows — are published under
[CC BY 4.0](LICENSE) for the docs and the [MIT license](samples/LICENSE) for the sample flows and any
code generated from them. You may use, modify, and ship code built from these samples in your own
products, commercial ones included.
