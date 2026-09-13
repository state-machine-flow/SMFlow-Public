# Changelog

All notable changes to SMFlow are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and SMFlow adheres to
[semantic versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
### Changed
### Fixed

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

