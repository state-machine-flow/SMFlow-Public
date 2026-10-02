# Lab 2 — "On your own" solution

```
Alarm = JamDetect OR NOT GuardClosed OR (StartButton AND NOT GuardClosed)
```

Two nodes added: an `and` (`forced`) and a second `or` (`fault2`). `NOT GuardClosed` is reused —
the existing `noguard` node fans out to both consumers rather than being duplicated.

```
smflow validate lab-02-solution.smflow
smflow build    lab-02-solution.smflow --target linux-x64 --emit-only
```

The generated `MainTask`:

```cpp
void MainTask(IO& io)
{
    const bool startButton = io.StartButton;
    const bool guardClosed = io.GuardClosed;
    const bool jamDetect = io.JamDetect;

    io.Motor = startButton && guardClosed && !jamDetect;
    const bool t6 = !guardClosed;

    io.Alarm = jamDetect || t6 || startButton && t6;
}
```

## The two questions

**How many nodes, how many statements?** Two nodes added, and *one* statement appeared — `const
bool t6`. The `and` and the `or` both folded into the `io.Alarm` expression, exactly like the
intermediate nodes in the main lab.

**Does `NOT GuardClosed` appear twice?** No. It is computed once into `t6` and used twice.

That second one is worth a moment. In the main lab, `!guardClosed` was written inline because it
had exactly one consumer. Here it has two, so the compiler hoisted it into a named temporary —
common subexpression elimination, which is an ordinary optimization that an ordinary C++ programmer
would also do by hand.

Notice the compiler made that decision on **value reuse**, not on graph shape. You did not draw
anything differently; `noguard` was already fanning out to two places. The emitted form changed
because the second consumer made hoisting worthwhile.

A nitpick worth noticing, since this series keeps claiming the output is review-grade: the final
expression leans on C++ precedence (`&&` binds tighter than `||`) rather than parenthesizing the
`startButton && t6` term. It is correct, and it is what a C programmer would read without pausing —
but it is the sort of thing you might flag in review of hand-written code.
