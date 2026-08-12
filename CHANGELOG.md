# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project aims to
follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] – 2026-08-12

### Added

- CI workflow running `pygamine`'s test suite, a real app-level test suite covering the 2048-style
  merge mechanic, and an app-level smoke test that boots `Game()` and cycles every panel.

### Changed

- Renamed the `pygame_core` submodule/dependency to `pygamine`.

### Fixed

- Editable `pygame-core` install not actually taking effect.
- A stale `pygamine` deep-path reference in `src/util/paths.py`'s docstring.

## [0.1.1] – 2026-07-08

- Added a window mode picker to Display Settings; fixed resize/layout bugs.
- Documented the Windows SmartScreen warning; storefront docs reorganized.

## [0.1.0] – 2026-07-07

Initial release. 2048-style building-merge game, migrated onto `pygame_core` and renamed to Highrise,
with a splash screen, PyInstaller build/release automation, and itch.io publishing.
