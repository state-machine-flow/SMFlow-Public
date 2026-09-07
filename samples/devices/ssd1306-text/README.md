# SSD1306 OLED Text Display Example

This example demonstrates how to use the **SSD1306 128x64 I2C OLED display** device to render static and dynamic text strings and counter telemetry on microcontroller targets (Raspberry Pi Pico, ESP32-S3) and in the SMFlow simulator.

## Overview

1. **Title Header**: An `SSD1306 Text` node outputs the static text `"SMFlow OLED"` on Line 0.
2. **Press Counter**: When `CountButton` is pressed:
   - The **Counter** block increments its current value (`CV`).
   - The **Create Payload** block packs `pressCount:int32:be` into binary bytes.
   - The dynamic `SSD1306 Text` node updates Line 2 with the formatted counter output.
   - Pressing `ResetButton` resets the counter to 0.
3. **Status Line**: A static `SSD1306 Text` node outputs `"Status: OK"` on Line 4.

## Wiring & Node Layout

```
CountButton (DI) ──► [CU] Counter [CV] ──► [in_pressCount] Create Payload [payload] ──► [text] SSD1306 Text (Line 2)
ResetButton (DI) ──► [R]

SSD1306 Text (Line 0, Text: "SMFlow OLED")
SSD1306 Text (Line 4, Text: "Status: OK")
```

## Device Configuration

- **Device Name:** `Oled`
- **Device Type:** `solomon:ssd1306` (128x64 Monochrome I2C OLED Display)
- **I2C Bus:**
  - Raspberry Pi Pico: `i2c0` (GP4 SDA / GP5 SCL)
  - ESP32-S3: `i2c0` (GPIO8 SDA / GPIO9 SCL)
  - Default I2C Address: `0x3C`

## Building and Simulating

```bash
# Build for Raspberry Pi Pico
smflow build examples/ssd1306-text --target rp2040-pico

# Build for ESP32-S3
smflow build examples/ssd1306-text --target esp32-s3

# Run in simulator
smflow sim examples/ssd1306-text
```
