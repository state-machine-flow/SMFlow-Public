# NOT gate

The smallest complete SMFlow program:

```
StartButton → NOT → Motor        i.e.  Motor = !StartButton
```

Three nodes, one boolean, one 10 ms periodic task. It exists to show the whole pipeline end to end —
graph, validation, IR, generated C++, native binary — with nothing else in the way.

## Run it

```
smflow simulate samples/basics/not-gate/project.smflow
smflow test     samples/basics/not-gate/project.smflow
smflow build    samples/basics/not-gate/project.smflow --target linux-x64
```

No hardware or `.iomap` is needed for the simulator. To run it on a board, add pin bindings for
`StartButton` and `Motor` and build for that target.
