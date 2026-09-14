# Modbus server status on a character display

The same Modbus TCP server as [`modbus-analog`](../modbus-analog/), with its three status counters
on a 20×4 character LCD.

This is a **commissioning tool**, not a control program. It answers the question you actually have
when a board is on the network and a client is getting nothing back: *is the scan running, is the
frame arriving, is it being rejected?* Each of those is a different fault with a different fix, and
without a display they look identical from the client end.

## What you see

```
Line 0   ModbusMsSinceRequest    milliseconds since the last valid request
Line 1   ModbusRequestCount      valid requests served since power-up
Line 2   ModbusErrorCount        malformed frames and exception responses
```

Read them in that order — each one only means something if the one above it is behaving.

| Line 0 | Line 1 | Line 2 | What it means |
|---|---|---|---|
| `2147483647` | 0 | 0 | Nothing has ever arrived. Expected before your first poll — see below. |
| Settles to your poll interval | climbing | 0 | **Working.** Polling every 500 ms reads ~510 ms: the interval plus one scan. |
| Stays `2147483647` | 0 | 0 | No octets are reaching the codec. Wrong address, wrong subnet, or no route — not a framing fault, or line 2 would move. |
| Stays `2147483647` | 0 | **climbing** | Frames arrive and are rejected. Check the unit id, and that you are using function **4**. |
| Blank or garbled | — | — | The LCD address is wrong. `0x27` vs `0x3F`; this says nothing about Modbus. |

**Line 0 is not a heartbeat.** It starts at `2147483647` and only ever moves when a request lands —
a server never contacted and one silent for an hour should drive the same fallback, so it starts
saturated by design. Before your first poll, all three lines read exactly as the first row above,
and that tells you nothing about whether the scan is running. Poll it and watch line 1 instead.

## The register map

Input registers, function code **4**, `ABCD` word order. Not holding registers — function 3 answers
exception 2.

| Address | Registers | Variable | Encoding |
|---|---|---|---|
| 30001 | 2 | `Channel1` | float32, volts on A0 |
| 30003 | 2 | `ModbusMsSinceRequest` | int32 |
| 30005 | 2 | `ModbusRequestCount` | int32 |
| 30007 | 2 | `ModbusErrorCount` | int32 |

One channel rather than four, because this sample is about the server rather than about the signals.
Only `Channel1` counts against the free tier's four-entry cap — status exports are exempt — so there
is room to add three more channels and still build unlicensed.

```
mbpoll -m tcp -a 1 -r 1 -c 8 -t 3 -0 192.168.1.50
```

Poll it twice. Line 0 should collapse toward zero and line 1 should increment, on the glass, as you
watch.

## Hardware

An Arduino Mega 2560 with a **W5100 Ethernet shield** and a **20×4 character LCD** on a PCF8574 I²C
backpack.

| What | Where | Note |
|---|---|---|
| Channel 1 | A0 | 0–5 V, 10-bit. A floating pin reads drifting noise, not zero. |
| Ethernet controller | `spi0`, CS **D10**, SD CS **D4** | The shield reaches SPI through the **ICSP header** — D11–D13 are the Uno's SPI and are *not* SPI on a Mega. |
| LCD | `i2c0` (D20 SDA / D21 SCL), **0x27** | |

Two settings you will probably have to change, both in **Settings → Devices**:

- **The LCD address.** `0x27` is a PCF8574T; a PCF8574**A**T is `0x3F`. They are indistinguishable
  without reading the chip marking, which is why SMFlow refuses to guess and the field starts empty
  on a fresh device. A wrong address is a blank screen and nothing else.
- **The IP and MAC.** The sample ships `192.168.1.50` and `DE:AD:BE:EF:FE:01`. The address must suit
  your network and the MAC must be unique on the segment.

## Building it

The Ethernet library is not bundled with the AVR core. Open **Settings → Tools** and press Install
beside *Ethernet library*, or from a terminal:

```
arduino-cli lib install "Ethernet"
```

Then:

```
smflow validate samples/applications/modbus-diagnostic/project.smflow
smflow build    samples/applications/modbus-diagnostic/project.smflow --target atmega2560-mega
```

Costs on an ATmega2560, measured: **20,150 bytes of flash (7%)** and **1,549 bytes of SRAM (18%)**,
leaving 6,643 bytes for the stack. The display is most of the difference against `modbus-analog`'s
16,800 / 1,048.

## Measured on hardware

An Elegoo Mega 2560 R3 with a W5100 shield, answering an independent Modbus TCP client:

| | |
|---|---|
| Request-to-response latency | 13 ms min, 20 ms max, **18 ms mean** |
| Repeated connections | six sequential connect-poll-close cycles, all answered |
| Off-map read | exception 2, not zeros |
| Holding-register read | exception 2 — this map serves none |
| Unknown function code | exception 1 |

18 ms matches the model: `ceil(frame / 64) x 2 x 10 ms` is 20 ms for a frame this size. The cost of
a tick is fixed at 64 octets in and out, which is what turns request size into latency rather than
into a cycle-time spike.

## Why the display and not a serial console

SMFlow's generated code prints nothing. There is a UART HAL for device buses, but no diagnostic
console — so on a headless board the only way to ask the firmware what it thinks it is doing is to
put it on something you can see. That is a real gap rather than a design choice, and it is why this
sample exists.
