# WS2812 Addressable RGB LED Status Indicator

This sample demonstrates how to control **Worldsemi WS2812 / WS2812B (NeoPixel)** addressable RGB LEDs over SPI MOSI.

## Overview

The flow monitors a machine alarm state and updates a multi-LED WS2812 status strip:
1. **Normal Operation:** When `AlertButton` is unasserted (`false`), the `ws2812-fill` block lights the entire strip solid **Green** (`R=0, G=255, B=0`), indicating normal process status.
2. **Alert Mode:** When `AlertButton` is pressed (`true`):
   - The strip turns solid **Red** (`R=255, G=0, B=0`).
   - The auxiliary `AlarmRelay` output is energized (`true`).

## Wiring & Node Layout

```
AlertButton (DI) ──┬──► [in] NOT [out] ────────► [enable] WS2812 Fill (Green: 0, 255, 0)
                   ├──► [enable] WS2812 Fill (Red: 255, 0, 0)
                   └──► [value] AlarmRelay (DO)
```

## Peripheral Configuration

- **Peripheral Name:** `StatusStrip`
- **Peripheral Type:** `worldsemi:ws2812` (WS2812 Addressable RGB LED)
- **Bus Kind:** SPI
- **Settings:**
  - `ledCount`: `8`
  - `colorOrder`: `GRB` (standard WS2812 / WS2812B)
  - `autoShow`: `true` (automatically pushes updated frames on scan)
  - `brightness`: `128` (50% global brightness)

### Hardware Connections

| Signal | Raspberry Pi Pico | ESP32-S3 | Description |
|---|---|---|---|
| **DIN** | `GP19` (SPI0 MOSI) | FSPI MOSI | WS2812 serial data in |
| **+5V / VBUS** | `VBUS` (Pin 40) | `5V` | LED power supply |
| **GND** | `GND` | `GND` | Common ground |
| **AlertButton** | `GP16` (Pull-Down) | `GPIO7` | Alarm push button |
| **AlarmRelay** | `GP17` | `GPIO8` | Auxiliary alarm beacon output |

> [!NOTE]
> WS2812 LEDs require a single high-speed data stream. In SMFlow, the driver maps each 800 kHz bit to 3 SPI bits transmitted via hardware SPI MOSI. No Chip Select (CS) line is required.

## Building and Testing

```bash
# Validate the flow
smflow validate samples/peripherals/ws2812-indicator/ws2812-indicator.smflow

# Build for Raspberry Pi Pico
smflow build samples/peripherals/ws2812-indicator/ws2812-indicator.smflow --target rp2040-pico

# Build for ESP32-S3
smflow build samples/peripherals/ws2812-indicator/ws2812-indicator.smflow --target esp32-s3

# Build for simulator
smflow build samples/peripherals/ws2812-indicator/ws2812-indicator.smflow --target simulator
```
