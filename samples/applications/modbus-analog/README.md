# Four analog channels, read over Modbus TCP

Four 0–5 V inputs on an Arduino Mega 2560, exported as four IEEE-754 floats that any off-the-shelf
Modbus client can read, plus a fault lamp that lights when the client goes away.

The register map is part of the program and the transport is part of the wiring. That split is the
whole design: retargeting this flow to another board changes the io map and moves no addresses.

## What it does

```
Channel1In (A0) ──► [Channel1]              ┐
Channel2In (A1) ──► [Channel2]              │  refreshed together as the
Channel3In (A2) ──► [Channel3]              │  coherent group "Channels"
Channel4In (A3) ──► [Channel4]              ┘

[ModbusConnected] ──► NOT ──► FaultLamp (D8)
```

There are no Modbus nodes on the canvas, and there is no way to add one. The graph writes ordinary
shared variables; a separate register map says which variable appears at which address. That is what
lets the same flow be rebuilt for another board without an integrator's register list moving.

## The register map

All values are read-only to the client — input registers, `ABCD` word order, big-endian per the
specification.

| Address | Registers | Variable | Encoding | Group |
|---|---|---|---|---|
| 30001 | 2 | `Channel1` | `float32` | Channels |
| 30003 | 2 | `Channel2` | `float32` | Channels |
| 30005 | 2 | `Channel3` | `float32` | Channels |
| 30007 | 2 | `Channel4` | `float32` | Channels |
| 30009 | 2 | `ModbusMsSinceRequest` | `int32` | Status |
| 30011 | 2 | `ModbusErrorCount` | `int32` | Status |

Six entries, and it still builds on the free tier: the cap is **four entries bound to a variable of
your own**, and the server's status variables are exempt. A fifth channel would be refused.

**If your client reads nonsense, check the word order first.** Much of the installed base expects
`CDAB` — the two words swapped. SMFlow will not guess: set `"wordOrder": "cdab"` on the map, or on
the single entry that needs it.

## Status variables

Turning the server on declares five read-only variables. They are ordinary shared variables, so
`variable-read` reaches them and the graph can act on them — which is how the fault lamp works.

| Variable | Type | Meaning |
|---|---|---|
| `ModbusConnected` | `bool` | A valid request arrived within the liveness window (5 s here). |
| `ModbusMsSinceRequest` | `int32` | Milliseconds since the last valid request. Saturating. |
| `ModbusLastException` | `int32` | The exception code last returned; `0` for none. |
| `ModbusRequestCount` | `int32` | Valid requests served since start. Saturating. |
| `ModbusErrorCount` | `int32` | Malformed frames and exception responses. Saturating. |

The counters saturate rather than wrapping, and `ModbusMsSinceRequest` starts saturated. A counter
that wrapped to zero would read as *just heard from the client* — the exact false negative a
communications watchdog exists to catch, arriving silently at a fixed interval after commissioning.

## Hardware

An **Elegoo Mega 2560 R3** (or a genuine Arduino Mega 2560) with a **W5100 Ethernet shield**.

| What | Where | Note |
|---|---|---|
| Channels 1–4 | A0–A3 | 10-bit against the 5 V rail |
| Fault lamp | D8 | An LED and a resistor is enough |
| Ethernet controller | `spi0`, CS on **D10** | The shield reaches SPI through the **ICSP header** — D11–D13 are the Uno's SPI and are *not* SPI on a Mega |
| SD card chip select | **D4** | Deselected at startup. An SD card nobody deselects corrupts the shared bus |
| SPI master | **D53** | Driven as an output, or the AVR drops out of master mode |

The shield's controller is named in `project.iomap`, not detected at run time. **A W5100 and a W5500
are not register-compatible** — read the silkscreen on the largest chip and set the device type to
match, or the board will build cleanly and never answer.

The MAC and the IP are yours to choose, on the controller in **Settings → Devices**. Neither is
defaulted. A MAC has to be unique on the segment, and a generated one would differ
between two builds of the same program. The address is static rather than DHCP because
`Ethernet.begin(mac)` blocks for up to a minute, and a board that never boots because a DHCP server
was down is not a machine anyone can commission.

## Building it

The Ethernet library is not bundled with the AVR core. Open **Settings → Tools** in the editor and
press Install beside *Ethernet library* — it sits with the board cores, and SMFlow installs it the
same way.

From a terminal instead:

```
arduino-cli lib install "Ethernet"
```

Either way, then:

```
smflow validate samples/applications/modbus-analog/project.smflow
smflow build    samples/applications/modbus-analog/project.smflow --target atmega2560-mega
```

## What it costs on the board

Measured by compiling this example for `arduino:avr:mega` with Ethernet 2.0.2 and AVR core 1.8.6:

| | |
|---|---|
| Flash | 16,800 bytes — 6 % of 253,952 |
| SRAM, static | 1,048 bytes — 12 % of 8,192, leaving 7,144 for the stack |

The server image itself is tiny: this map is 12 registers, 24 bytes. Most of that 1 KB is the two
260-byte frame buffers and the Ethernet driver.

## Reading it

With any Modbus TCP client — `mbpoll`, QModMaster, a SCADA package:

```
mbpoll -m tcp -a 1 -t 3 -r 1 -c 8 -0 192.168.1.50
```

`-t 3` is input registers, `-r 1` is 30001, `-0` uses zero-based addressing on the wire.

## What to expect of the timing

The task runs every 10 ms and the server moves **64 octets per tick**, in and out. That is a
deliberate trade.

Fixing the octet count makes the cost of a scan a constant you can budget. On this board every octet
is an SPI transaction against the controller, so "one frame per tick" would not be a bound at all —
it would be an average with a bad tail, and a 260-octet frame landing in a 10 ms task is a 10–20 %
cycle spike chosen by a remote client.

What you pay for it is latency, and it is the number you will measure:

```
response time ≈ ceil(frame / 64) × 2 × scan period
```

A 20-register read answers in roughly 80 ms. That is fine for SCADA telemetry and wrong for a
closed control loop — which Modbus was never the right wire for anyway.

## The guarantee, exactly

A client is served a **snapshot**, refreshed at a barrier after the tasks run, never live variable
storage. A float read while a task was updating it would be corrupt *and numerically plausible*,
which is the worst available failure because nothing downstream can detect it.

One coherent group refreshes per scan. So:

- The four channels always agree with each other — they are one group.
- The channels and the status registers may be one scan apart.
- A single client read spanning both groups still mixes epochs. That is the honest edge of the
  guarantee, not a bug.
