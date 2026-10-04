# Persistent Button Counter Example

This example demonstrates how to persist and retain application state (a button press counter) across power cycles using SMFlow's persistent storage subsystem ([ADR 0050](../../docs/adr/0050-persistent-storage-for-shared-variables.md)) and report the count via the serial debug console ([ADR 0036](../../docs/adr/0036-serial-console-and-transmit-node.md)).

## Overview

1. **On Boot / Restore:**
   - The runtime automatically restores `PressCount` from non-volatile persistent storage before the first scan cycle runs.
   - The **Persist Status** node asserts `restored = true`.
   - A **Rising Edge** node detects `status.restored` going true on boot and pulses `restore_edge.Q` for exactly one scan cycle.
   - The **OR** node (`or_send`) passes this pulse to the **Serial Tx** node (`console.send`).
   - The **To Text** node formats `"Count: {}\n"` from the restored `PressCount` variable, transmitting it immediately over the serial debug console (e.g. `Count: 2`).

2. **On Button Press / Change:**
   - When the user presses the button (`Button = true`), the **Select** node switches from `Zero` (0) to `One` (1).
   - The **Update Variable** node atomically adds 1 to `PressCount`.
   - The **Persist Save** node detects the rising edge on `trigger` and saves the `retained` memory region.
   - The **OR** node passes the button press to `console.send`.
   - The **Serial Tx** node detects the rising edge on `send` and outputs the updated count to the serial debug console (e.g. `Count: 3`).

---

## Wiring & Graph Flow

```
Button (DI) ──┬──► [cond] Select [out] ──► [value] Update Variable ("PressCount", add)
              │       ▲       ▲
              │       │       └── [value] Variable Read ("Zero")
              │       └────────── [value] Variable Read ("One")
              │
              ├──► [trigger] Persist Save ("retained")
              │
              └──► [a] OR [out] ──► [send] Serial Tx ("Console")
                    ▲                     ▲
Persist Status ──► [IN] Rising Edge [Q] ──┘    [data]
 ("retained")                                   ▲
                                                │ [text]
Variable Read ("PressCount") ──► [value] To Text ("Count: {}\n")
```

---

## Free-Tier Compliance

This flow contains **12 nodes**, complying strictly with SMFlow's **12-node free tier limit** (`LicenseEntitlements.FreeFlowNodeLimit = 12`). Anyone can open, simulate, and compile this project without a license.

---

## Target Storage & Serial Console Mapping

SMFlow maps the logical `retained` storage region and the logical `Console` serial endpoint to each target:

| Target | Hardware Store | Media / Technology | Serial UART Bus | Baud Rate |
|---|---|---|---|---|
| `simulator` | `sim-store` | Host filesystem (`smflow_store_retained.bin`) | `virtual.uart0` (stderr) | 9600 |
| `heltec-lora32-v3` | `nvs0` | ESP32-S3 NVS partition | `uart0` (USB CDC serial) | 115200 |
| `esp32-s3` | `nvs0` | ESP32-S3 NVS partition | `uart0` (Default TX=GPIO43) | 115200 |
| `rp2040-pico` | `flash0` | Dedicated top flash sector | `uart0` (GP0/GP1) | 115200 |
| `atmega328-nano` | `eeprom0` | On-chip 1 KB EEPROM | `uart0` (D0/D1 USB serial) | 115200 |
| `atmega328-uno` | `eeprom0` | On-chip 1 KB EEPROM | `uart0` (D0/D1 USB serial) | 9600 |
| `atmega2560-mega` | `eeprom0` | On-chip 4 KB EEPROM | `uart0` (D0/D1 USB serial) | 9600 |
| `linux-x64` | `file0` | Local configuration file | `console` (stdout) | 115200 |

---

## Verifying in the Simulator

### 1. Run Automated Graph Tests
```bash
smflow test samples/applications/persistent-counter/counter.smtest
```

### 2. Interactive Power-Cycle Simulation

Build the desktop simulator:
```bash
smflow build samples/applications/persistent-counter/persistent-counter.smflow --target simulator
./generated/persistent-counter.exe
```

In the simulator console:
```text
step 1
step 1
set Button true
step 1
set Button false
step 5
set Button true
step 1
set Button false
step 5
quit
```

On the serial console (stderr), notice the count increments:
```text
Count: 1
Count: 2
```
`smflow_store_retained.bin` has now captured the retained count (`2`).

Now start the simulator again (simulating reboot / power-on):
```bash
./generated/persistent-counter.exe
```
Execute scan cycle:
```text
step 1
```
The console immediately outputs:
```text
Count: 2
```
The count was restored from storage and transmitted over serial on boot!
Pressing the button advances the count further:
```text
set Button true
step 1
set Button false
step 5
```
Serial output:
```text
Count: 3
```
