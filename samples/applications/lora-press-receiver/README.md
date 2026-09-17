# LoRa Press Receiver Example

This example demonstrates receiving binary LoRa packets over a UART interface, unpacking structured telemetry data using an instance-derived payload schema, and emitting the parsed result to the console.

It pairs directly with the transmitter in `applications/lora-press-counter`.

## Overview

When the transmitter emits a packet containing a 32-bit counter value (`pressCount:int32:be`):
1. The **Serial RX** block (`LoRa`, bound to the Raspberry Pi UART `/dev/ttyAMA0` at 9600 baud) receives the octets into an `smflow::Bytes<256>` buffer and asserts `received` for that scan cycle.
2. The **Unpack Payload** block unpacks the 32-bit big-endian integer `pressCount` and asserts `valid` if the packet is at least 4 bytes.
3. The **AND** gate ensures both a fresh packet was received and that its length matches the schema.
4. The **To Text** block formats the integer into human-readable text (`Received LoRa count: {}\n`).
5. The **Serial TX** block (`Console`, bound to `stdout`) transmits the formatted line when triggered by the gate output.

## Wiring Diagram

```
Enable (DI) ──► [enable] Serial RX (LoRa) [data] ─────► [payload] Unpack Payload [out_pressCount] ──► [value] To Text [text] ──► [data] Serial TX (Console)
                                         [received] ─┬► [a] AND [out] ───────────────────────────────────────────────────────────► [send]
                                                     │
               [valid] Unpack Payload ───────────────┴► [b]
```

## Schema Configuration

- **Node Type:** `unpack-payload`
- **Schema:** `pressCount:int32:be`
- **Input Port:** `payload` (`DataType.Bytes`)
- **Derived Output Port:** `out_pressCount` (`DataType.Int32`)
- **Validation Output Port:** `valid` (`DataType.Bool`)

## Hardware Setup (Raspberry Pi + Waveshare SX1268 LoRa HAT)

- **Target:** `linux-arm64` (Raspberry Pi 3/4/5)
- **Radio Interface:** Waveshare SX1268 LoRa HAT via Raspberry Pi 40-pin header UART (`/dev/ttyAMA0` / `/dev/serial0` on GPIO 14/15)
- **Baud Rate:** 9600 baud, 8N1 (default UART interface rate for Ebyte E22 module)
- **Console Interface:** Standard output (`stdout`) via `console` bus
