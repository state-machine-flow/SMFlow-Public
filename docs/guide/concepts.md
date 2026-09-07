# Concepts

> **Draft.** This page is outlined but not yet written. Track it in
> [issues](https://github.com/state-machine-flow/SMFlow-Public/issues).

- **Graph** — the flow; it is the source code, not a description of one
- **Node** — a typed operation with named input and output ports
- **Connection** — a wire from one output port to one input port; types must match exactly, and no conversion is ever inserted silently
- **Type** — bool and the numeric primitives
- **Task** — a named unit of execution with a fixed period; nodes execute in a deterministic order within it
- **Target** — the board or platform the graph is compiled for
- **Hardware profile / iomap** — the binding of logical resources to physical pins or terminals, kept out of the flow so one flow can serve several boards
