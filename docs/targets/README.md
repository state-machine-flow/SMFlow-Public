# Targets

A target is what SMFlow compiles your flow into a binary for. Run `smflow targets` to see the list
your installed build supports.

| Target | ID | Class |
|---|---|---|
| Desktop simulator | `simulator` | Development only |
| Linux x64 | `linux-x64` | Static native binary |
| Linux ARM64 | `linux-arm64` | SBCs such as Raspberry Pi |
| Arduino Opta | `opta` | Industrial PLC |
| Raspberry Pi Pico | `rp2040-pico` | MCU |
| Arduino Nano RP2040 Connect | `rp2040-nano-connect` | MCU |
| ESP32-S3 | `esp32-s3` | MCU with wireless |
| Arduino Nano (ATmega328) | `atmega328-nano` | 8-bit MCU |
| Portable C++ | `portable` | Vendor-neutral C++17 source you integrate yourself |

Per-target pages cover the pinout, capabilities and limits, host toolchain setup, and how to flash.
They are written as the pages are needed — open an issue for one that's missing.
