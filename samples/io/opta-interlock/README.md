# Opta interlock

The [motor interlock](../../logic/motor-interlock) on an Arduino Opta — an industrial PLC form factor
with screw terminals and relay outputs.

Logical resources are bound to Opta terminals in `project.iomap`. The flow is identical to the
simulator version; only the bindings change.

## Wiring

See `project.iomap` for terminal assignments, and
[the Opta target guide](../../../docs/targets/opta.md) for input voltage ranges and relay ratings.

Mains-voltage loads are outside what this sample assumes. Prove the logic on low-voltage first.

## Build and deploy

```
smflow build  samples/io/opta-interlock/project.smflow --target opta
smflow deploy samples/io/opta-interlock/project.smflow --target opta
```
