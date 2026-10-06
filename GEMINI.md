# SMFlow Workspace Guidelines

## Sample Creation
All sample projects and flows must be created in this public samples repository under:
`samples/`

### Directory Organization
- `samples/basics/<sample-name>/` — Minimal single-concept samples (e.g., gates, basic counters)
- `samples/logic/<sample-name>/` — Combinational and latching behavior
- `samples/timing/<sample-name>/` — Delays, periods, timers, sequencers
- `samples/io/<sample-name>/` — Hardware board and pin-specific flows (e.g., Arduino Opta, Raspberry Pi Pico)
- `samples/peripherals/<sample-name>/` — Displays and sensors (I²C / SPI)
- `samples/applications/<sample-name>/` — End-to-end applications (e.g., LoRa, Modbus)

### Sample File Conventions
Each sample folder must contain:
- `<sample-name>.smflow`: Project flow file with explanatory `"comment"` fields on each functional node
- `<sample-name>.iomap`: Pin/terminal mappings when targeting hardware
- `<sample-name>.smtest`: Test suite asserting expected behavior
- `README.md`: Explaining the flow, hardware connections, and CLI test/build commands

When adding new samples, update the catalog tables in `samples/README.md`.
