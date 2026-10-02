# Parts list

**Labs 1–7 and 11 need no hardware.** Everything runs in the desktop simulator. If you only want
the fundamentals, stop reading here.

## Required for the hardware labs (8, 9, 10, 12, capstone)

| Qty | Part | Used in | Approx. |
|---|---|---|---|
| 1 | Raspberry Pi Pico (or Pico H, pre-soldered headers) | 8, 9, 10, 12, capstone | $5 |
| 1 | Micro-USB cable (data, not charge-only) | all | — |
| 1 | Solderless breadboard, 830 tie-point | all | $5 |
| 1 | Jumper wire kit, male-male | all | $5 |
| 4 | Tactile pushbutton, 6 mm through-hole | 8, 9, capstone | $2 |
| 4 | LED, 5 mm, assorted colors | 8, 9, 10, capstone | $2 |
| 4 | 330 Ω resistor (LED series) | 8, 9, 10, capstone | $1 |
| 4 | 10 kΩ resistor (pull-down) | 8, 9, capstone | $1 |
| 1 | 10 kΩ linear potentiometer | 10 | $2 |
| 1 | Passive piezo buzzer | 10 | $2 |
| 1 | SSD1306 OLED, 128×64, I²C, 4-pin | 12, capstone | $6 |

Total: roughly **$30** if you buy the parts individually, less from a starter kit.

Buy the **passive** piezo, not an active buzzer. An active buzzer generates its own tone and
ignores the waveform you give it, which defeats the point of Lab 10.

## Optional

| Part | Why |
|---|---|
| Arduino Opta (any variant) | Lab 9 shows the same graph on an Opta. Worth it if your day job is PLCs and you want to see SMFlow next to a DIN-rail device, but it is ~$150 and the lab works without it. |
| ESP32-S3 dev board | Also used in Lab 9's retarget comparison. ~$10. |
| Any I²C sensor from the catalog | Lab 12's "on your own" swaps the sensor. `smflow` lists what is supported — a BME280 or an APDS-9960 are both good choices. |
| Logic analyzer (8-channel, ~$10) | Not required, but the fastest way to convince yourself about scan timing in Lab 3 once you are on hardware. |

## Toolchains

Installed per target, not all at once. Each lab names what it needs.

| Target | Needs |
|---|---|
| simulator | A host C++17 compiler: `g++`, `clang++`, or MSVC |
| linux-x64 / linux-arm64 | The matching cross-compiler on `PATH` |
| rp2040-pico, opta, esp32-s3, AVR boards | `arduino-cli` with the board's core installed |

See [installation](../docs/getting-started/installation.md) and the
[target guides](../docs/targets/).
