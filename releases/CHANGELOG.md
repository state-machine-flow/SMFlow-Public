# Changelog

All notable changes to SMFlow are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and SMFlow adheres to
[semantic versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
### Changed
### Fixed

## [0.9.12-beta1] - 2026-10-02

### Added

- **Values that survive a power cycle.** A shared variable can be marked persistent and comes back
  after the power is cycled, instead of restarting at its declared initial value - what a calibration
  coefficient, a commissioned setpoint, an hour meter or a totalizer has always needed. Tick it in the
  variable editor and choose a region: `config` is written rarely, by a person, at commissioning time;
  `retained` is written by the program as it runs. They are kept apart because flash and EEPROM wear
  out, and the two kinds of data do not wear them at the same rate.
- **Three nodes to drive it.** `persist-save` writes a region, `persist-clear` returns it to its
  declared defaults, and `persist-status` reports whether the values were restored, defaulted or
  found corrupt - so a flow can raise an alarm when the stored record was rejected rather than trust
  numbers it should not. A write happens only when you trigger one: nothing is saved behind your back,
  and the cost sits where you put it in the scan. All three carry the usual `busy` / `done` / `error`
  ports and a region picker.
- **Every target has somewhere to put it.** Internal EEPROM on the AVRs, an NVS partition on the
  ESP32-S3, a reserved internal flash sector on the RP2040 and the Opta, a file written
  temp-then-rename on Linux so a power cut cannot leave half a record, and a file in the simulator -
  so retention can be tried on the desktop before the hardware exists. External parts are supported
  too: a **24LC256 I2C EEPROM** and an **MB85RC I2C FRAM** bind like any other device.
- **Store bindings in Project Settings.** A persistence section says which store holds each region on
  each target, beside the existing IO binding table. Left blank, a target with exactly one candidate
  store allocates itself, so the common board needs no decision at all.
- **CAN, over the MCP2515.** The MCP2515 controller with an MCP2551-class transceiver is a peripheral
  you bind on any SPI-capable board, with `can-tx`, `can-rx` and `can-status` nodes. Bit timing is
  worked out at build time from the crystal you declare and the bitrate you ask for, so an unreachable
  combination is a build error naming the rates you can have - not a bus that silently never
  acknowledges. Frames per scan are budgeted like any other asynchronous device, so a busy bus cannot
  stretch a scan. Bus-off is reported, not hidden: `can-status` exposes the error counters and the
  bus-off flag, and recovery is requested by the flow, because rejoining a bus is a control decision.
- **A comment node.** A standalone block of text you can drop anywhere on the canvas and move like a
  node, for the paragraph that belongs to the whole flow rather than to one node. It has no ports, it
  is documentation only, and it cannot change a line of the generated C++.

## [0.9.11-beta1] - 2026-09-29

### Added

- **Group boxes, for organising a crowded flow.** Select some nodes and press **Ctrl+G** (or
  *Edit > Group Selection*) to draw a labeled box around them. Drag the title bar to move the box
  and everything inside it as one undoable step, drag the bottom-right corner to resize,
  double-click the title to rename, and press Delete to remove the box - its nodes stay where they
  are. A group is decoration: it owns no nodes and cannot change what your project builds.
- **Lasso multi-select.** Hold **Ctrl** and drag on empty canvas to sweep a rectangle over a
  cluster; every node it touches joins the selection. Ctrl-clicking a single node still toggles it,
  and dragging the background without Ctrl still pans.
- **Notes on a node.** Each node has a `[+]` button on its lower edge that opens a comment block
  attached to the node. Click the block to type, Escape to abandon the edit, and the button again to
  fold it away. The text is saved in the project, so the reason a threshold is 47 lives beside the
  node. Comments are documentation only and never change the generated C++.
- **Serial endpoints have a UI.** **Project > Serial Ports...** declares a logical endpoint by name,
  picks its UART bus and baud rate, and shows the endpoints and buffer sizes configured for each
  target - no more editing the `.smflow` by hand to add a `Console`.
- **Deploy to a Linux controller over the network.** **Build > Deploy** sends the generated C++ to
  the controller, compiles it there, installs a systemd unit and restarts the service, so the
  program survives a power cycle. Each step reports as it happens, and a compile that fails there
  returns the compiler's own output.
- **Controllers you configure, not just boards we find.** The **Deploy to** picker lists attached
  boards and configured network machines together, with a **Manage...** row to add, edit, remove and
  test them. **Test connection** reports the controller's architecture and whether it has a C++
  compiler - the two things a deployment depends on. Password sign-in is supported, which is what a
  stock Raspberry Pi image has; tick **Remember** and it is encrypted for your Windows account.
  Controllers are stored on your computer, never in the project, and no passphrase is kept.
- **The controller's log, in the editor.** After a network deployment the service log follows itself
  into the output pane. **Build > Follow Controller Log** (F8) starts it any time, **Stop Following**
  ends it, and **Check service** shows a running / stopped / failed badge on demand.
- **The Heltec WiFi LoRa 32 (V3) is a build target.** Its SX1262, OLED and Vext power switch are on
  the pins the board wires them to, so a project picks `heltec-lora32-v3` rather than writing seven
  pin bindings by hand. A radio on this board needs `tcxoVoltageMv` set to `1800`.
- **Radio settings live on the peripheral.** Frequency, spreading factor, bandwidth, coding rate,
  preamble, sync word, transmit power and TCXO supply are configuration on the binding. They all
  have to match at the far end, and a mismatch is silent - so check them first when a link carries
  nothing.
- **A purchased license actually activates.** This build carries the production license issuer, so
  a key issued for a purchase verifies and unlocks Pro. Earlier builds trusted no issuer: every
  license was refused and every installation ran as Free, whatever had been bought. If you bought a
  license before this release, install this build and activate again - your existing key works.
- **License keys are emailed.** Both a purchase and the site's "send me my key again" recovery now
  deliver by email.

### Changed

- **The free tier allows two serial endpoints, not one.** One link to the world plus the console to
  watch it on. A cap of one meant that the moment a free program talked to a radio, a GPS or an
  RS485 sensor it lost the console it was being debugged with.
- **SMFlow Pro is $500 as an introductory price**, regular price $800. There is no end date on the
  introduction: a license bought at $500 is perpetual on the usual terms and is never re-priced.
- Peripherals are now called peripherals, and the board or machine you deploy to is called a
  controller. The editor menu is **Project > Peripherals...**, the toolbar reads **Deploy to**, and
  **Build > Deploy** replaces "Deploy to Device".
- Projects and io maps save a `peripherals` key where they used to save `devices`. Existing
  projects still open: a file written under the old name is read, converted, and written back under
  the new one the next time it is saved, so nothing needs editing by hand.
- Generated C++ emits `namespace peripherals` instead of `namespace devices`. Rebuild rather than
  relinking against old object files.
- `smflow devices` is now `smflow controllers`, since it lists attached boards rather than
  peripherals. The old verb still works for now.
- For AI assistants: the MCP tool `list_devices` is now `list_peripherals`, and the authoring
  operations are `add_peripheral`, `rename_peripheral`, `remove_peripheral`,
  `set_peripheral_binding` and `clear_peripheral_binding`.
- The `samples/devices/` folder is now `samples/peripherals/`.

### Fixed

- **The SX1262 now actually transmits.** A LoRa radio in a project used to compile to a simulation: a
  two-scan countdown that raised Done, reported a fixed -65 dBm and 9.5 dB, and - if the same program
  also received - handed the payload straight back to itself. It issued no SPI transaction, so a
  board could report a successful send while nothing went out over the air. It has a real driver now,
  and a transmission it cannot confirm reports Error rather than Done.
- **A Linux target no longer refuses serial outboxes that fit a Raspberry Pi a thousand times over.**
  Linux had inherited a 256-octet outbox budget sized for an ATmega328, so two 256-octet endpoints
  failed with SMF0057 on a machine with a gigabyte of memory. Linux now budgets 64 KiB.
- **Shared peripheral helpers are emitted once, not once per peripheral type.** A project driving two
  different I2C peripherals produced a translation unit with two copies of the same register, CRC and
  conversion helpers.
- **For AI assistants: `describe_project` reported every live editor session as empty.** Node,
  connection, variable and peripheral counts came back as nought while the name, target and revision
  beside them were right. Headless mode was never affected.

## [0.9.10-beta1] - 2026-09-15

### Added

- **AI assistants can author flows.** `smflow mcp` starts a Model Context Protocol server that
  Claude Desktop, Claude Code, Cursor, VS Code and Windsurf can connect to. An assistant can read a
  project, ask what node types and targets this build actually has, look up a board's pinout, and
  propose changes to the graph. It authors from what the server reports, not from what it
  remembers, so it cannot invent a node or a pin that does not exist.
- **Every proposal is reviewed before it lands.** Changes arrive in the editor as a staged proposal
  with a plain summary and a ghosted preview on the canvas, and nothing is applied until you accept
  it. A "Trust AI edits for this session" toggle is available when you want hands-free iteration;
  it is in-memory only and is off again next launch.
- **Headless mode.** `smflow mcp --project <path>` works on a project file with no editor running,
  for scripting and CI. In that mode there is no review step — proposals apply directly.
- **Connect an AI client, from Settings.** The dialog gives the exact `smflow` path for this
  installation and a ready-to-paste configuration for each supported client, along with the file it
  belongs in. See `docs/guide/ai-assistants.md`.
- **Worked examples ship inside the binary.** The server hands a connecting assistant a short
  authoring brief plus example flows, so its guidance always matches the node catalogue this build
  reports. No network access is involved.
- **CLI authoring verbs.** `smflow new`, `smflow add-node`, `smflow connect` and `smflow apply`
  build a project from a script without opening the editor.
- **Undo and redo.** `Ctrl+Z` / `Ctrl+Y`, with readable labels for what is being undone. Applying a
  change and undoing it restores the project file byte for byte.

### Notes

- The control channel the editor exposes is loopback-only, carries a per-session bearer token, and
  stops with the editor. Deploying to hardware is never available through it.

## [0.9.9-beta1] - 2026-09-14

### Added

- **A serial console in the editor.** The bottom panel is tabbed — **Build** keeps the diagnostics
  and toolchain output, **Serial** shows what the board is saying. Pick a port, press Attach, and
  the editor watches for boards arriving and leaving. The port is held only while attached, so
  uploads and other tools on the machine can still open it.
- **`serial-tx`, so the graph chooses when to send.** Its `send` input is a rising edge: a condition
  held true transmits once, not once per scan. It reports `sent`, `busy`, and a saturating count of
  frames dropped for want of outbox room — a link that cannot keep up says so rather than stretching
  the scan.
- **Serial endpoints are declared hardware.** A project names an endpoint, binds it to a UART, and
  sets baud rate and outbox size in the `.iomap`. The graph names the endpoint by id, so moving a
  program to another board changes which UART carries it and nothing else.
- **`to-text` takes a format template.** Defaulting to `{}`: `frame count: {}\n` renders
  `frame count: 42` and a newline, `{0.00} V` renders `42.00 V`. Escapes are `\n`, `\r`, `\t`,
  `\\`, `{{` and `}}`; anything else is a validation error.
- **A resizable, floatable output panel.** A splitter resizes the bottom panel, and **⇱ Float**
  moves it into its own window when a console wants more height than the editor can spare.
- **Linux targets print to `stdout`.** An endpoint named as the console is the process's own output
  rather than a UART, so a `linux-x64` build logs without needing a terminal.
- **`samples/basics/serial-debug`** — a counter, a format template and a `serial-tx` on a timed
  task, showing the same output in the simulator, on `stdout`, and at 9600 baud from an ATmega328.

### Changed

- The free tier allows one serial endpoint. The console viewer itself is not gated; this limits how
  many UARTs one program may drive.

### Fixed

- Pulling the USB cable mid-read is now reported as a disconnect instead of leaving the console
  quiet with no explanation.

## [0.9.7-beta1] - 2026-09-14

### Added

- **Modbus TCP server.** A project declares a register map that binds shared variables to addresses,
  and the graph reaches those variables through the variable nodes it already has — there are no
  Modbus nodes on the canvas. Holding and input registers, function codes 3, 4, 6 and 16, over an
  Ethernet shield on an Arduino Mega 2560. Encodings (`float32`, `int32`, `int16`, scaled `int16`)
  and word order (`ABCD`/`CDAB`) are always declared, never inferred. Sample:
  `samples/applications/modbus-analog`.
- **Ethernet controllers as devices.** `wiznet:w5100` and `wiznet:w5500` are device types a project
  selects and binds to a SPI bus. Addressing is `static` or `dhcp`; the DHCP client is a state
  machine stepped once per scan, so nothing in the scan ever waits on the network.
- **Status as read-only shared variables.** `ModbusConnected`, `ModbusMsSinceRequest`,
  `ModbusLastException`, `ModbusRequestCount`, `ModbusErrorCount`, `EthernetControllerOk`,
  `EthernetAddressed` and `EthernetIpAddress` — so "the client went away, fall back to a safe state"
  is something a flow can express. Counters saturate rather than wrap.
- **Modbus map editor.** Settings → Modbus Map (Ctrl+Shift+M) edits the register map in place,
  assigns addresses automatically, flags overlaps, and exports the register sheet as CSV or Markdown.
- **Device properties page.** Settings → Devices renders a field for each setting a device type
  declares — address, MAC, IP — validated as you type instead of at build time.
- **Arduino Uno R3 target** (`atmega328-uno`), with the pins the Uno's headers actually bring out.

### Notes

- The free tier serves Modbus, capped at four entries bound to a variable of your own; status
  exports are exempt.
- Building a Modbus project needs the Arduino `Ethernet` library. Settings → Tools now lists and
  installs it.
- Modbus RTU, coils and discrete inputs, multiple unit ids, and the client/master role are not in
  this release; a project asking for one is refused at validation.

## [0.9.6-beta1] - 2026-09-13

### Added

- **Arduino Mega 2560 target** (`atmega2560-mega`), with its full pin set, timers, ADC channels,
  external interrupts, and four hardware UARTs.
- **PWM output.** A `pwm-output` node drives a hardware PWM pin directly. A pin's channel is a
  property of the I/O resource rather than inferred from the data type.
- **Tone output.** A `tone-output` node drives a piezo or speaker from a frequency and an enable,
  claiming the pin's timer for the duration.
- **A `select` node** — chooses between two values of the same type on a boolean input.
- **HD44780 character displays** over I²C through a PCF8574 backpack, with the per-character I²C
  cost accounted for in the bus budget.

### Changed

- A device node's caption shows the settings a wire has not taken over, so several display nodes in
  one task are distinguishable on the canvas.

## [0.9.5-beta1] - 2026-09-13

### Added

- The simulator panel lists the project's shared variables alongside the I/O, with each one's live
  value updating as the program runs. Boolean variables can be toggled, and any variable can be
  written while the simulation is running.

### Changed

- Variable read and write nodes take their port type from the variable they name rather than from
  the generic declared type, so port colors, compatible-port highlighting, and connection
  validation all follow the variable's real type.
- Dropping a new variable node onto the canvas reuses an existing shared variable that nothing
  references yet, instead of always creating another one.

## [0.9.4-beta1] - 2026-09-13

### Added

- Terms of Sale, License Agreement, Privacy Policy, and Refund Policy pages on smflow.co, plus a
  contact page.
- An `/examples` screenshot tour on the site, linked from the header and footer.

### Changed

- SMFlow Pro is priced at $300.
- Pro checkout is not open yet. `/purchase` shows a "coming soon" state, because key delivery and
  activation are not live end to end.

### Fixed

- Settings tells you a pin is already spoken for while you are picking it, instead of letting the
  build refuse the project later. A pin held by another signal or by a device reads
  "GP15 — used by Radio (reset)" in the list, the row holding it is outlined, and the tab says how
  many pins are contested. The I/O Mapping and Devices tabs check against each other, so a graph
  output and a device's reset line can no longer quietly land on the same pin.
- A device left without one of the pins its part requires — an SX1262's busy, dio1, or reset, say —
  now says so on its card in Settings. Previously it looked configured and failed at build time.
- Dragging the window between monitors of different scaling no longer leaves the Settings
  selectors' click targets away from the controls they belong to.
- The generic Windows icon is replaced with the actual SMFlow app icon across the executable
  resources, window titlebar and taskbar, and the installer.
- Settings: the pin option selectors line up in one column instead of stepping in and out row by
  row, and the Close button sits at the lower right of the dialog.

## [0.9.3-beta1] - 2026-09-08

A maintenance release. The application itself is unchanged in how it compiles and runs your
programs; what moved is licensing, the website, and one new hardware plug-in.

### Added

- MaxBotix ultrasonic rangefinder plug-in, so distance sensors can be dropped into a graph.

### Changed

- Purchases and license activation now run through the new licensing service.
- The product now lives at **smflow.co**. Download and update links point there.

### Fixed

- Corrected the download links on the website, which pointed at the wrong release assets.

## [0.9.1-beta1] - 2026-09-07

The first public build of SMFlow. Windows x64, self-contained — there is no .NET runtime to install
first — and it updates itself in place from this release channel.

### Added

- Draw a control program as a node graph, and compile it ahead of time to ordinary C++17. The
  target runs no interpreter, no scripting engine, and nothing from SMFlow.
- Targets in this build: simulator, Linux x64, Arduino Opta, ESP32, RP2040, and AVR.
- Step the program in the simulator and watch values move, without any hardware attached.
- Read the generated source. It is meant to survive a firmware review, and the same project always
  generates byte-identical output.
- The About box offers a support link and a "copy version info" button. The copied text carries the
  version, edition, and OS, and deliberately carries nothing that identifies you or your machine.

### Fixed

- Generated simulator source no longer emits string helpers the program never calls. A graph whose
  inputs were all numeric left `ParseBool` defined and unused, which failed the build under
  `-Werror=unused-function`.

### Known limits

- **Every install is capped at 12 nodes per flow.** The licensing server is not stood up yet, so no
  Pro license can be issued or validated, and the editor falls back to Free.
- Windows only. The compiler targets Linux, but the editor is packaged for Windows x64 in this
  build.
- Beta: the project file format may still change between beta builds.
