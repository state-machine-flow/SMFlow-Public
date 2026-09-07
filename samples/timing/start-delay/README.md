# Start delay

An on-delay: the output asserts only after the input has been continuously true for a set time, and
drops immediately when the input drops.

The delay is counted in task periods, so the timing follows the task's declared period rather than
wall-clock guesswork. See [tasks and timing](../../../docs/guide/tasks-and-timing.md) for what
SMFlow does and does not guarantee here.

## Run it

```
smflow simulate samples/timing/start-delay/project.smflow
smflow test     samples/timing/start-delay/project.smflow
```
