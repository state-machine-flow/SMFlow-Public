# Lab 4 — "On your own" solution

A low-level alarm at 20%, alongside the existing high alarm at 80%.

Three nodes added — a `variable-read` of a new `LowSetpoint`, a second `compare` with operator
`<`, and a `LowAlarm` output — plus a `LowAlarm` binding in the `.iomap` for each target.

```
smflow validate lab-04-solution.smflow
smflow build    lab-04-solution.smflow --target linux-x64 --emit-only
```

## The answers

### 1. How many times is `io.TankLevel` read?

**Once.**

```cpp
const float tankLevel = io.TankLevel;
...
io.HighAlarm = tankLevel > t2;
...
smflow::append_bytes(t15, smflow::to_text(tankLevel, 1));
...
io.LowAlarm = tankLevel < t22;
```

Three consumers, one read, at the top of the scan. That is the input snapshot doing its job: every
consumer in this scan is looking at the same number. If the sensor is noisy and drifts across the
setpoint between the two comparisons, the comparisons still cannot disagree with each other —
because there is only one value to disagree about.

This is a bigger deal than it looks. A hand-written version of this loop that called a `readAnalog()`
helper in three places would have three different samples, and a high alarm and a low alarm could
in principle both be true. Here that is structurally impossible.

### 2. One shared helper, or two literal comparisons?

Two literals, inline:

```cpp
io.HighAlarm = tankLevel > t2;
io.LowAlarm  = tankLevel < t22;
```

No comparison function, no operator enum, no dispatch. The operator property is resolved at compile
time into the C++ operator itself.

That is the payoff for making the operator a **property** rather than a port. If the operator could
change at runtime, the generated code would need to carry all six comparisons and select between
them. Because it cannot, each compare node costs exactly one machine comparison — the same as if
you had written the `if` by hand.

Note also that the two comparisons did **not** get common-subexpression-eliminated into anything
shared, because there is nothing shared to eliminate: different operators, different operands.
Contrast with Lab 2, where the repeated `!guardClosed` *was* hoisted. The compiler folds what is
genuinely identical and leaves the rest alone.

### A detail worth noticing

`LowAlarm` is emitted at the *bottom* of the task, after the console logic, rather than next to
`HighAlarm` where it logically belongs:

```cpp
    (void)serial::ConsoleAdmit(t13 && !t16, t15);
    state.s2_prev_send = t13;
    const float t22 = LoadShared_LowSetpoint();

    io.LowAlarm = tankLevel < t22;
```

That is the declaration-order tiebreak from Lab 2. The low-alarm chain is independent of
everything else, so dataflow imposes no constraint, and the nodes were appended last. The program
is identical — both outputs are committed together at the bottom of the scan — but it is a good
reminder that the emitted order is "a valid order", not "the order you would have chosen".

If you care about reading order in the generated source, that is a reason to add nodes in the
order you want them to appear. It is a readability preference, not a correctness one.
