# SMFlow documentation

The manual for SMFlow — a visual programming environment that compiles node-and-wire graphs into
native C++ with no runtime on the device.

## Getting started

- [Installation](getting-started/installation.md) — installers, prerequisites, toolchains
- [Your first flow](getting-started/first-flow.md) — build and run `Motor = !StartButton`
- [Licensing and activation](getting-started/licensing.md) — Free vs. Pro, activating a key

## Using SMFlow

- [Concepts](guide/concepts.md) — graphs, nodes, ports, types, tasks
- [The editor](guide/editor.md) — canvas, palette, inspector, keyboard
- [Tasks and timing](guide/tasks-and-timing.md) — periodic tasks, what determinism guarantees
- [Simulation](guide/simulation.md) — running and stepping a flow on the desktop
- [Building and deploying](guide/building-and-deploying.md) — targets, artifacts, flashing
- [Testing flows](guide/testing.md) — `.smtest` files and `smflow test`
- [Working with an AI assistant](guide/ai-assistants.md) — connecting Claude, Cursor, Copilot, and friends
- [The CLI](guide/cli.md) — `validate`, `build`, `simulate`, `test`, `deploy`, `targets`, `devices`
- [Project file format](guide/project-format.md) — what `.smflow` and `.iomap` contain
- [Troubleshooting](guide/troubleshooting.md)

## Reference

- [Node library](nodes/) — every node, its ports, and its semantics
- [Targets](targets/) — per-board pinout, capabilities, and toolchain setup
- [Generated code](reference/generated-code.md) — what the compiler emits and why
- [Glossary](reference/glossary.md)
- [FAQ](reference/faq.md)

## Contributing to these docs

Corrections and clarifications are welcome — see [CONTRIBUTING.md](../CONTRIBUTING.md).
