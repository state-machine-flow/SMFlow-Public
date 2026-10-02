# Lab 1 — "On your own" solution

`Motor = StartButton AND GuardClosed`.

Four nodes: two `digital-input`, one `and`, one `digital-output`.

```
smflow validate lab-01-solution.smflow
smflow build    lab-01-solution.smflow --target linux-x64 --emit-only
```

The generated `application.cpp`:

```cpp
void mainTask(IO& io)
{
    const bool startButton = io.StartButton;
    const bool guardClosed = io.GuardClosed;

    io.Motor = startButton && guardClosed;
}
```

Two locals, one assignment, in dataflow order. The `and` node became `&&`, exactly as the `not`
node became `!` — for the same reason.

If you predicted this before running the build, you have the model the rest of the series is built
on.
