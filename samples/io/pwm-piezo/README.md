# PWM and piezo — a duty cycle and a tone on an Arduino Mega 2560

Two output kinds that are neither a relay nor a voltage: a **PWM duty cycle** on D6, and a **tone**
on D8 driving a passive piezo.

```
Speed (analog-input, A0) ──────────────► Drive  (pwm-output,  D6)
AlarmHz (variable, 2700) ──────────────► Buzzer (tone-output, D8)
```

Four nodes, which builds on the free tier.

## Wiring

| | |
|---|---|
| Board | Arduino Mega 2560 R3 (`atmega2560-mega`) |
| Speed | **A0** — a 10 kΩ potentiometer between 5 V and GND, wiper to A0 |
| Drive | **D6** — Timer4. A motor driver's PWM input, or an LED through a resistor |
| Buzzer | **D8** — a passive piezo disc, other leg to GND |
| Supply | 5 V |

**A passive piezo, not an active buzzer.** An active buzzer contains its own oscillator: apply
voltage and it sounds, at one fixed pitch. That is a `digital-output` and nothing here applies to it.
A passive piezo or speaker needs a driven waveform, which is what `tone-output` is for. The two parts
look nearly identical, and nothing in the program can tell them apart — the choice is yours to
declare.

A piezo element is capacitive and high-impedance, so it drives straight off a pin. A **magnetic**
buzzer or a small speaker draws more than a pin should give and wants a transistor.

**2700 Hz is not arbitrary.** A piezo disc has a resonant frequency, typically 2–4 kHz, where it is
dramatically louder. An alarm wired at 440 Hz that "barely makes a sound" has not found a bug.

## What the two outputs mean

**`Drive` carries a duty cycle from 0.0 to 1.0 — not volts.** A PWM pin switches between off and the
board's logic level; what voltage the load sees depends on its inductance and on whatever filtering
sits in front of it, which is the panel's business. Values outside 0.0–1.0 are clamped where the pin
is written, visibly, in the generated source:

```cpp
int DutyCounts(float duty)
{
    if (duty <= 0.0f) return 0;
    if (duty >= 1.0f) return kPwmFullScale;
    return (int)(duty * (float)kPwmFullScale + 0.5f);
}
```

That is why `pwm-output` is a separate node from `analog-output`, which carries volts out of a real
DAC. Letting one stand for the other would not fail to compile — a 3.3 that meant volts would clamp
to a duty of 1.0 and run a motor flat out. That is why the two are separate node types rather than one.

**`Buzzer` carries a frequency in hertz, and zero or below is silence.** The write is guarded on
change, because `tone()` is not idempotent: called every scan with an unchanged frequency it reloads
the compare register and restarts the waveform, which is audible as a buzz rather than a clean tone.

```cpp
if (io.Buzzer != lastTone_Buzzer)
{
    if (io.Buzzer > 0.0f)
    {
        tone(D8, (unsigned int)(io.Buzzer + 0.5f));
    }
    else
    {
        noTone(D8);
    }

    lastTone_Buzzer = io.Buzzer;
}
```

Both outputs start at zero in `InitializeHardware` — `analogWrite(D6, 0)` and `noTone(D8)` — for the
reason the digital path already gives: a machine that energizes before the first scan has decided
anything is a machine that starts by itself.

## The pot's useful range is the first volt

`Speed` is an analog input, so it reads the **terminal voltage**: 0–5 V on a Mega, against the
board's own 5 V rail as the ADC reference. The duty clamps at 1.0, so the whole 0–100 % span lives in
the first volt of pot travel, and everything above it is full speed.

That is honest rather than convenient, and it is exactly where SMFlow is missing a piece: scaling
0–5 V onto 0.0–1.0 needs an arithmetic node, and the node library has none yet. In the **simulator**
there is no such awkwardness — set `Speed` to `0.35` and read it back as a 35 % duty.

## Timers

On a Mega 2560 the tone takes **Timer2**, which also drives PWM on **D9 and D10**. Bind a
`pwm-output` to either of those while a tone is claimed and the build warns, naming both — the duty
compiles but cannot reach the pin. `Drive` is on D6, off Timer4, so nothing here contends.

**Timer0 is reserved and can never be claimed.** It carries `millis()`, which the scan model, every
timer node and the watchdog are built on.

Arduino also sounds **one tone at a time, full stop**: with a tone already sounding, `tone()` on a
second pin has no effect at all — not a race, not a garbled pitch, nothing. A second `tone-output`
node is therefore a compile error rather than a silently dead node.

## Building

```bash
smflow validate samples/io/pwm-piezo/project.smflow
smflow build    samples/io/pwm-piezo/project.smflow --target atmega2560-mega
smflow build    samples/io/pwm-piezo/project.smflow --target simulator
```

The Mega build compiles with `arduino-cli` to roughly 6.3 KB of flash and 120 bytes of RAM.

## Caveats

- **The buzzer sounds continuously.** Gating it on a fault would need a node that chooses between two
  floats on a condition, and SMFlow has no select node yet — the only `float32` sources are an analog
  input, a shared variable and a device read, none of them conditional. Unplug the piezo before
  leaving this running on your desk.
- **Frequency is not configurable on a PWM output.** The duty runs at the board's `analogWrite`
  default, about 490 Hz on D6. Setting it is an exclusive claim on Timer4 and costs D7 and D8 their
  duty, so it is a decision about pins rather than only a port.
- **Below about 31 Hz the AVR tone path cannot produce a waveform.** The frequency is computed at run
  time, so there is nothing for the validator to reject.
- **The ADC reference is the board's own 5 V rail**, not a precision reference, so a sagging USB
  supply shifts every reading.
- **The Opta refuses this project**, and correctly: its outputs are relays and it declares no PWM.
  Retargeting fails loudly rather than quietly changing what the number means.
