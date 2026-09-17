# LoRa Press Counter

Counts button presses, sends each count over LoRa, and shows it on the board's display.

The receiving half of this is [lora-press-receiver](../lora-press-receiver).

## What it does

Press the button and:

1. **Counter** increments its count (`CV`).
2. **Create Payload** packs it as a 32-bit big-endian `pressCount` into a `Bytes<256>` buffer.
3. **SX1262 TX** sees the rising edge on `trigger` and transmits the packet.
4. `busy` is true while the packet is on the air, and lights the LED.
5. `done` pulses for one scan when the radio confirms the packet went out. `error` latches if it did
   not — a radio that stops answering fails rather than holding `busy` forever.
6. **To Text** formats the count as `Sent: 12`, and **SSD1306 Text** writes it to line 0.

```
Button (DI) ─┬─► [CU] Counter [CV] ─┬─► [in_pressCount] Create Payload [payload] ─► [payload] SX1262 TX (Radio)
             └─► [trigger] ─────────┼──────────────────────────────────────────────►
                                    └─► [value] To Text [text] ─► [text] SSD1306 Text (Oled)

                          SX1262 TX ─► [busy]  ─► Busy  (DO)
                                    ─► [done]  ─► Done  (DO)
                                    ─► [error] ─► Error (DO)
```

`Input1` resets both counters.

## Boards

The sample builds for two targets, and which one you pick decides how much you have to wire.

### Heltec WiFi LoRa 32 (V3) — `heltec-lora32-v3`

The radio and the display are soldered to this board, so the only thing to wire is a button.

| Signal | Pin | Note |
|---|---|---|
| Button | GPIO7 | to 3V3, pulled down internally |
| Input1 | GPIO19 | resets both counters, pulled down |
| Busy | GPIO35 | the on-board LED |
| Done | GPIO2 | |
| Error | GPIO3 | |

The radio is on GPIO8–GPIO14 and the display on GPIO17/GPIO18 with reset on GPIO21. The board also
powers its display from Vext on GPIO36, which the target switches on at start-up — that is what
picking the board rather than the bare chip buys you, and why this section does not mention it.

### A bare ESP32-S3 with modules wired to it — `esp32-s3`

Wire it however you like and say so in `project.iomap`, under the `esp32-s3` section. The pins
recorded there are one working arrangement, not a requirement.

## Radio settings

In `project.iomap`, under the `Radio` peripheral. **Every one of these must match at the receiving
end.** A mismatch is silent: the receiver simply never hears a packet, and nothing at either end
reports a problem.

| Setting | Value |
|---|---|
| `frequencyHz` | `915125000` — inside the US ISM band (902–928 MHz). Europe uses 863–870. Use what you are licensed for. |
| `spreadingFactor` | `7` |
| `bandwidthKhz` | `125` |
| `codingRate` | `5` (4/5) |
| `syncWord` | `private` — `public` is for joining a LoRaWAN network |
| `txPowerDbm` | `14` |
| `preambleSymbols` | `8` |
| `tcxoVoltageMv` | `1800` on a V3; omit it on a module with a plain crystal |

**`tcxoVoltageMv` is not optional on a Heltec V3.** Its radio runs from a 1.8 V TCXO on the SX1262's
own DIO3. The default is a plain crystal, because telling a crystal-only module to wait for a TCXO
leaves it dead — so a board with one has to say so. Get it wrong and the part reports
`XOSC_START_ERR`, which the driver reads back at start-up and raises on the `error` output.

## Payload

Four bytes, big-endian. The receiver has to unpack the same shape:

```
pressCount:int32:be
```

## Pairing with a receiver

The transmitter is verified working on a Heltec V3: a receiver three feet away measured the
carrier 51 dB above its noise floor at the configured frequency.

**Pairing it with an Ebyte E22 UART module is unresolved.** An E22 is not a bare SX1262 — it is an
SX1262 behind its own MCU running Ebyte's protocol, and matching frequency alone is not enough. A
session spent on it confirmed the RF arrives and is never decoded, across four spreading factors and
both sync words. What remains untested is the packet framing: explicit versus implicit header, and
the address bytes Ebyte's transparent mode appears to expect inside the payload. If you are pairing
with an E22, budget for that rather than assuming it is a settings change.

Two receivers avoid the question entirely: a second board running the same SMFlow driver, or a bare
SX1262 module driven directly. Both ends then share one implementation and one set of parameters.

## Checking it works

The display counts up and the LED blinks for the few milliseconds each packet is on the air. That is
the transmitter doing its job — it is **not** evidence that anything received it. LoRa gives a
transmitter no acknowledgement, so `done` means the SX1262 reported the packet sent, not that
anything heard it. To know that, look at the receiving end.

If the receiver hears nothing, check in this order: both ends on the same frequency, spreading
factor, bandwidth, coding rate and sync word; then antennas actually fitted; then the payload shape.
