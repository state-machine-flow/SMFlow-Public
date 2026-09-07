# The CLI

`smflow` is the command-line face of the same compiler the editor uses. It installs alongside the
editor — one download gives you both — and is what you reach for to run graph tests, analyze a build,
or drive SMFlow from a script or CI job.

You never *need* it to use SMFlow. The editor validates, builds, simulates, and deploys on its own,
calling the compiler in process rather than shelling out to this executable. The two are peers over
one compiler, which is why they cannot disagree about what a project means.

## Where it is

The installer does not put `smflow` on your `PATH`. It lives in the install directory alongside the
editor:

```
%LocalAppData%\SMFlow\current\smflow.exe
```

To use it as a bare `smflow` command, add that directory to your `PATH`. Note that a Velopack update
installs into a new directory and repoints `current`, so add the `current` path rather than a
version-stamped one.

## Commands

| Command | Does |
|---|---|
| `smflow validate <project>` | Type- and connection-checks the graph |
| `smflow build <project> --target <id>` | Generates C++ and compiles it |
| `smflow simulate <project>` | Runs the flow in the desktop simulator |
| `smflow test <project>` | Runs the project's `.smtest` suites |
| `smflow deploy <project> --target <id>` | Builds and flashes an attached board |
| `smflow analyze <project>` | Reports on the generated program |
| `smflow report <project>` | Produces a build report |
| `smflow targets` | Lists the targets this build can compile for |
| `smflow devices` | Lists attached boards |
| `smflow license status` | Shows the current license and what it grants |

## Exit codes

`0` on success. A non-zero code distinguishes a usage error from a validation failure from a license
refusal, so a CI job can tell "the graph is wrong" from "this build needs Pro".

## The free tier and the CLI

The node limit is enforced in the compiler, not in the editor's UI, so `smflow build` refuses an
over-limit flow exactly as the editor does. There is deliberately no command-line flag to override
it.

Note that `smflow validate` does **not** check the limit — validation is a static check of the graph
itself, and reports on a flow you may not be able to build yet. The limit applies when code is
generated.
