# Motor interlock

A motor that runs only when the start command is present *and* nothing is inhibiting it — the
canonical safety interlock, expressed as combinational logic.

This is the first sample where validation matters: leave an input unconnected and the compiler
refuses to generate code rather than guessing a default.

## Run it

```
smflow simulate samples/logic/motor-interlock/project.smflow
smflow test     samples/logic/motor-interlock/project.smflow
```

Hardware variants of the same logic live in [`../../io/pico-interlock`](../../io/pico-interlock) and
[`../../io/opta-interlock`](../../io/opta-interlock).
