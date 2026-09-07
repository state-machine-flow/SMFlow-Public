# Pico interlock

The [motor interlock](../../logic/motor-interlock) running on real hardware — a Raspberry Pi Pico,
with the logical inputs and outputs bound to GPIO pins in `project.iomap`.

The flow itself is unchanged from the simulator version. Only the bindings differ: that separation is
the point of the `.iomap` file.

## Wiring

Check `project.iomap` for the exact pin assignments, then wire switches to the input pins (to ground,
with pull-ups enabled) and an LED or contactor driver to the output pin.

## Build and deploy

```
smflow build  samples/io/pico-interlock/project.smflow --target rp2040-pico
smflow deploy samples/io/pico-interlock/project.smflow --target rp2040-pico
```

Hold BOOTSEL while connecting the Pico so it enumerates as a mass-storage device.
