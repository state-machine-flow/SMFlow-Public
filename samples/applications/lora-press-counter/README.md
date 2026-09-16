# LoRa Press Counter Example

This example demonstrates creating and transmitting binary LoRa packets with an instance-derived payload schema and an asynchronous SX1262 LoRa transceiver.

## Overview

When the physical **Button** is pressed:
1. The **Counter** block increments its current count (`CV`).
2. The **Create Payload** block packs the 32-bit big-endian integer `pressCount` into an `smflow::Bytes<256>` binary buffer.
3. The **SX1262 TX** block detects the rising edge on `trigger` and transmits the packet over the air via the Semtech SX1262 LoRa transceiver.
4. While transmission is in progress across multi-cycle scans, `busy` is asserted, lighting the **TxLed**.
5. When transmission finishes, `done` pulses true for one cycle and `busy` returns to false.

## Wiring Diagram

```
Button (DI) ──┬──► [CU] Counter [CV] ──► [in_pressCount] Create Payload [payload] ──► [payload] SX1262 TX (Radio) ──► [busy] ──► TxLed (DO)
              └──► [trigger] ──────────────────────────────────────────────────────────┘
```

## Schema Configuration

- **Node Type:** `create-payload`
- **Schema:** `pressCount:int32:be`
- **Derived Input Port:** `in_pressCount` (`DataType.Int32`)
- **Output Port:** `payload` (`DataType.Bytes`, 4 bytes total length)

## Peripheral Configuration

- **Peripheral Instance:** `Radio`
- **Peripheral Type:** `semtech:sx1262` (Asynchronous SPI LoRa Transceiver)
