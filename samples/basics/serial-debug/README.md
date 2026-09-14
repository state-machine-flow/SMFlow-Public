# Serial debug

Printing a value to a serial console, which is how you find out what a flow is actually doing on a
board with no debugger attached.

`Sensor` is read every scan and printed twice a second as a labelled, formatted line:

```
sensor: 3.27 V
sensor: 3.28 V
sensor: 3.26 V
```

In the editor those lines appear in the **Serial** tab of the bottom panel — from the simulator when
you press F5, and from a real board when you pick its port and press **Connect**.

## How it works

Four nodes and a serial endpoint.

- **Analog Input `Sensor`** samples the pin once at the start of the scan, as a `float32`.
- **To Text** renders it. Its `format` property is `sensor: {0.00} V\n` — that is the whole of the
  formatting, and the next section is about it.
- **Serial TX `Console`** transmits the rendered line.
- **Blink** (500 ms on, 500 ms off) drives the Serial TX `send` input, so a line goes out twice a
  second instead of ten times a second.

**Sending on an edge is the important part.** `send` transmits on the false-to-true edge, not for
as long as it is held, so a value held true does not re-send every scan. The task period is 100 ms;
without the Blink you would get ten lines a second, and at 9600 baud on an Uno most of them would
be dropped.

`Run` gates the Blink, so the console is quiet until you switch it on.

## The format

`to-text` takes a template with exactly one placeholder standing for the value:

| Format | `3.2712` renders as |
|---|---|
| `{}` | `3.27` — the value alone, using the node's `decimals` |
| `sensor: {}` | `sensor: 3.27` |
| `sensor: {0.00} V` | `sensor: 3.27 V` |
| `{0.0}` | `3.3` |
| `{0.0000}` | `3.2712` |
| `sensor: {0.00} V\n` | the line above, then a newline |

Two spellings of the placeholder, and only two:

- **`{}`** — the value, with as many decimal places as the node's `decimals` property says.
- **`{0.00}`** — the value with exactly that many fractional digits, overriding `decimals`.

`{0}` is refused rather than guessed at. It is the C# spelling for "argument zero", so someone who
has written C# reaches for it meaning *the value* — but under a precision grammar it would mean *no
decimal places*, silently truncating the float. Two readings and no way to tell which was meant, so
the editor asks you to say which.

Escapes are `\n`, `\r`, `\t` and `\\`, plus `{{` and `}}` for literal braces. Anything else is an
error, not a passed-through backslash.

**Try changing it.** Edit the format, rebuild, and watch the console change. Nothing else in the
flow moves.

## The newline is not decoration

It is the only thing in this flow that marks where one reading ends and the next begins. With the
default `{}` format, consecutive frames arrive with nothing between them:

```
3.273.283.263.29
```

A console with no separator has to be read by counting digits. Put `\n` at the end of every debug
format.

## Where the port is configured

Not on the node. The node names `Console`; `project.iomap` says what `Console` is on each board:

```json
"serial": {
  "atmega328-uno": {
    "Console": { "bus": "uart0", "baud": 9600, "txCapacity": 64, "txBufferOctets": 64 }
  }
}
```

On the Uno that is the same USB connection the sketch was uploaded over. Retargeting to `uart1` at
115200 is an edit to that file; the flow does not change.

No host port name — `COM5`, `/dev/ttyACM0` — appears in either file. Those differ from machine to
machine, and one in a project file would mean the same flow built differently on two desks. The
editor remembers which port you were watching as a local preference instead.

## Running it

```
smflow simulate samples/basics/serial-debug/project.smflow
> set Run true
> set Sensor 3.271
> step 30
```

```
smflow build samples/basics/serial-debug/project.smflow --target atmega328-uno
smflow build samples/basics/serial-debug/project.smflow --target linux-x64
```

Under the simulator, frames go to the program's `stderr` — `stdin` and `stdout` are carrying the
simulator's own protocol.

## Wiring

| Signal | Uno | What |
|---|---|---|
| `Run` | D2 | A switch or jumper to 3.3 V/5 V; the console is quiet while it is low |
| `Sensor` | A0 | Anything analog — a potentiometer wiper is enough |
| `Console` | USB | The uart0 the board already enumerates as |

## What this does not do

**One value per line.** A Serial TX node takes one `data` connection, so `x=1.0 y=2.0` on one line
is out of reach. A line per value is the shape this buys, and for debugging it is usually enough.

**Nothing on the board parses a format string.** The template is split by the compiler into a
literal, the number, and a literal, so no `printf` is linked and a format can never disagree with
its argument at runtime. The cost is that a format is a build input: changing it is a rebuild, not a
setting.

**Drops are real.** At 9600 baud a 500 ms scan carries about 480 octets. A flow that emits more than
that, scan after scan, drops whole frames rather than sending half of one — and a bigger outbox only
means the drops happen later with staler data. Wire the Serial TX `dropped` output somewhere you
will see it, and read `smflow build --report` for the octets-per-scan ceiling next to the outbox
size.
