# Stopwatch

A one-button stopwatch. `StartStop` starts the count on a press and stops it on the next press;
`Clear` zeroes the reading.

Elapsed time accumulates into `ElapsedTenths`, an `int32` counting tenths of a second — so 10.2
seconds reads as `102`. The count is in whole tenths rather than a float on purpose: see
[Why tenths, not seconds](#why-tenths-not-seconds) below.

## How it works

The task period is 100 ms, and each scan that the stopwatch is running adds 1 to `ElapsedTenths`.
Time is counted in scans rather than read from a clock — see
[tasks and timing](../../../docs/guide/tasks-and-timing.md) for what that does and does not
guarantee.

- **Toggle** turns a press into a state. Its `CLK` sees the raw button, and it flips on the
  false-to-true edge, so holding the button does nothing extra.
- **Select** turns that state into a number: `OneTenth` (1) while running, `Zero` while stopped. It
  feeds an **Update Variable** set to *add*, which is the only way to accumulate into a variable
  atomically.
- **Clear** does two things at once. It is wired to the Toggle's `R`, which is reset-dominant — `Q`
  is false on that scan, so nothing is added while Clear is held. It also selects the current
  `ElapsedTenths` into a second **Update Variable** set to *subtract*, which brings the variable to
  exactly zero. Subtracting what was just read is how a graph zeroes a variable without a second
  writer racing the first.

There is no constant node, so the two literals the Selects need come from declared variables:
`OneTenth` (1) and `Zero` (0).

`Running` mirrors the Toggle's state so it can be asserted in a test or watched in the simulator.

## Why tenths, not seconds

Adding `0.1` to a `float32` a hundred times does not land on exactly `10.0` — `0.1` has no exact
binary representation, and the error compounds with every scan. That is real behavior on the target,
not a simulator artifact, and it is the reason a stopwatch counts whole units.

`int32` tenths are exact, so `stopwatch.smtest` asserts equality rather than ranges. Converting to
seconds for a display (`102` → `10.2`) is a division, and a display is the right place for it — it
happens once, on the value being shown, instead of accumulating error into the state itself.

## The scan a press lands on counts

Pressing `StartStop` starts the count on that same scan, so a press followed by ten scans reads
`11`, not `10`. The Toggle's `Q` goes true during the scan that sees the edge, and the add is
downstream of it. `stopwatch.smtest` asserts this directly rather than papering over it.

## Run it

```
smflow simulate samples/timing/stopwatch/project.smflow
smflow test     samples/timing/stopwatch/project.smflow
```
