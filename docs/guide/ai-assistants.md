# Working with an AI assistant

SMFlow ships an MCP server, so an AI assistant — Claude Desktop, Claude Code, Cursor, Windsurf, or a
VS Code extension like Cline or Copilot — can read your project, check it, propose changes, and build
it. You describe what the machine should do; the assistant wires the graph.

This is opt-in and off until you turn it on.

## What an assistant can and cannot do

It can:

- read the graph, the tasks, the shared variables, and the configured peripherals
- look up which nodes exist, which targets are supported, and what pins a board actually has
- run validation and read the errors back
- **propose** changes — nodes, wires, parameters, tasks, variables, peripheral bindings
- build the project and report what the compiler said

It cannot:

- flash or deploy to hardware. There is no deploy tool, in any mode. Deployment stays a deliberate
  act you perform from the editor or the CLI.
- change your project behind your back. With the editor open, every proposal is shown to you as a
  diff and a ghosted canvas preview, and nothing lands until you accept it.
- reach anything beyond SMFlow. The channel it talks to is bound to `127.0.0.1` on an ephemeral
  port, refuses non-loopback requests, and forbids cross-origin ones entirely.

Two things are worth saying plainly. SMFlow compiles to firmware that runs real machinery, so treat
a proposed change the way you would treat a pull request from a competent stranger: read it. And an
assistant is good at wiring and terrible at knowing what your machine must never do — interlocks,
stop conditions, and failure behaviour are yours to specify and yours to check.

## Before you start

1. **Install SMFlow.** The MCP server is `smflow mcp`, part of the CLI that installs beside the
   editor. See [Installation](../getting-started/installation.md).
2. **Turn on automation** if you want the assistant to work with the editor you have open. In the
   editor: **Settings → Local automation & AI agent control → Allow local automation**.

   Leave it off if you only want headless use, described below.

## The quick way

In **Settings**, beside that toggle:

- **Connect an AI client…** shows the exact path to this installation's `smflow`, a ready-to-paste
  configuration for each supported client, and the file that client expects it in. Copy, paste,
  restart the client.
- **AI setup guide…** opens this page.

That dialog is generated from your actual install, so its path is correct for your machine. If you
would rather do it by hand, read on.

## Setting it up by hand

`smflow mcp` speaks JSON-RPC 2.0 over stdio. Your client starts it; you never run it yourself.

Every client wants the same shape of configuration:

```json
{
  "mcpServers": {
    "smflow": {
      "command": "C:/Users/you/AppData/Local/SMFlow/current/smflow.exe",
      "args": ["mcp"]
    }
  }
}
```

Two details matter:

- **Use the full path.** The installer does not put `smflow` on your `PATH`, so a bare `"smflow"`
  works only if you added it yourself. Point at the `current` directory rather than a
  version-stamped one — an update installs alongside and repoints `current`.
- **Use forward slashes.** A backslash is an escape character in JSON. A raw Windows path usually
  makes the client fail to load its config without telling you why.

Where the configuration goes:

| Client | Where |
|---|---|
| Claude Desktop | `%APPDATA%\Claude\claude_desktop_config.json` (Windows), `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) |
| Claude Code | `claude mcp add smflow -- <path to smflow> mcp` |
| VS Code (Cline, Roo Code, Copilot) | the extension's MCP settings file, e.g. `cline_mcp_settings.json` |
| Cursor | `.cursor/mcp.json` in the project, or the global agent settings |
| Windsurf | the Cascade MCP settings file (`mcp_config.json`) |

Restart the client after editing its configuration. Most only read it at startup.

## Two ways to run

### With the editor open

This is the default. Start the editor, open your project, tick **Allow local automation**, and the
assistant discovers the running session and works against what is on your canvas.

Every proposal it makes is staged for review. You see a summary of the change, the operations it
contains, and a preview of the graph with the new nodes ghosted in, and you accept or reject it.
Accepted changes go onto the normal undo stack, so `Ctrl+Z` reverses them like anything else.

If you are iterating quickly and the assistant is getting it right, **Trust AI edits for this
session** lets proposals apply without the prompt. It resets when you close the editor — trust is
never persisted.

### Headless, with no editor

Point the server at a project file and it works on that file directly:

```
smflow mcp --project path/to/project.smflow
```

There is no editor to review anything, so proposals are applied and saved as they arrive. This is
the right mode for scripted or batch work, and the wrong mode for anything you have not put in
version control. Commit first.

Everything else is the same — the same tools, the same validation, and still no deploy.

## What the assistant knows

It does not guess at your hardware. It asks:

| Tool | What it answers |
|---|---|
| `list_node_types` | Every node this build has, with ports and types |
| `list_targets` / `describe_target` | Supported boards; a board's pins, ADC and PWM channels, buses, clock |
| `read_graph` / `describe_project` | The project as it is now |
| `list_peripherals` / `list_variables` | Configured peripherals and shared variables |
| `get_diagnostics` | Validation errors and warnings |
| `list_examples` / `get_example` | Worked flows shipped with this build |
| `propose_changes` | Submits a batch of edits for review |
| `build` | Compiles and reports |

The server also hands the assistant a short authoring brief when it connects, covering the workflow
and the rules — notably that it must look nodes and pins up rather than assume them. Both the brief
and the examples ship inside the binary, so they always match the version you installed, and none of
it needs network access.

## Getting good results

- **Say what the machine does, not what nodes to place.** "The conveyor runs while the start button
  is held and the guard door is closed, and stops immediately if either fails" gets a better graph
  than a list of nodes.
- **State the target early.** Pin counts, PWM availability, and bus support differ enough between
  boards to change the design.
- **Be explicit about safety.** Name the interlocks and the failure behaviour. An assistant will not
  infer that a stop input is wired active-low, or that an output must fail to the de-energised state.
- **Ask it to validate.** "Validate and fix anything that comes back" costs one turn and catches most
  wiring mistakes.
- **Point it at a sample.** The [samples](../../samples/) directory is real, working projects, and
  "build something like the motor interlock sample, but with two guard doors" is a very effective
  prompt.

## Troubleshooting

**The client shows no SMFlow tools.** Its configuration did not load. Check the path, check the JSON
is valid, check it uses forward slashes, and restart the client.

**"No active SMFlow editor sessions found."** Either the editor is not running, or **Allow local
automation** is off. Turn it on and ask again — the assistant does not need restarting.

**It says the revision conflicts.** You edited the graph after it read it. Ask it to re-read and try
again; refusing a stale change is the safety mechanism working.

**A proposal is refused.** Read the reason. Usually it named a node type or port that does not exist
in your build, or tried to connect two incompatible types. SMFlow never silently converts a type —
the graph needs an explicit conversion node.

**It wants to deploy.** It cannot. Build with the assistant, then deploy yourself from the editor or
with `smflow deploy`.

## See also

- [The CLI](cli.md) — the same compiler, without an assistant
- [Concepts](concepts.md) — graphs, ports, types, tasks
- [Tasks and timing](tasks-and-timing.md) — what determinism guarantees
- [Samples](../../samples/) — working projects to point an assistant at
