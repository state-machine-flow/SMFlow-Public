# Contributing

This repository holds SMFlow's public documentation and sample flows. The product source is closed,
so pull requests here cover docs, samples, and release notes — not the compiler or editor.

## Reporting bugs and requesting features

Use [Issues](../../issues/new/choose). For a bug, include:

- SMFlow version (**Help → About**, or `smflow --help` header)
- Operating system
- The target you were building for
- The `project.smflow` that reproduces it, if you can share it
- What you expected, and what happened instead

## Improving the documentation

Edit the Markdown under `docs/` and open a pull request. Keep to the existing voice: short sentences,
concrete examples, no marketing language. Anything version-specific should say which version it
applies to.

## Contributing a sample

A sample earns its place by teaching one thing clearly.

1. Create a folder under the right category in `samples/`.
2. Name the files after the folder: `<name>.smflow`, a `README.md`, a `<name>.iomap` if it targets
   hardware, and a `.smtest` if the behavior is worth asserting. (Naming the flow after the sample
   is what makes it readable in the editor's recent-projects list; the `.iomap` must share the
   `.smflow` base name, since the editor pairs them by name on disk.)
3. Do **not** commit generated C++, build output, or editor scratch files.
4. Verify it before opening the PR:

   ```
   smflow validate samples/<category>/<name>/<name>.smflow
   smflow test     samples/<category>/<name>/<name>.smflow
   ```

5. Add a row to the catalog in [samples/README.md](samples/README.md).

The sample README should state what it demonstrates, the wiring or pin assignment it assumes, and the
exact command to run it.

## Licensing of contributions

Documentation contributions are published under CC BY 4.0; sample flows under MIT. By opening a pull
request you agree your contribution is licensed on those terms.
