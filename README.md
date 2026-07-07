# Highrise

An isometric city-builder where same-level buildings merge `2048`-style. Build, merge, expand, and advance through ages — Python + [pygame-ce](https://github.com/pygame-community/pygame-ce).

![Gameplay](docs/preview.gif)

## Gameplay

Place buildings on the isometric grid, then slide them with WASD/arrows to merge same-level neighbours into a higher-level building (just like 2048). Higher-level buildings produce more income. Spend income to construct new buildings, expand the land, or advance to the **next age** to unlock better building tiers.

### Screenshots

| Menu | Build mode | Inspection |
|------|------------|------------|
| ![](docs/screenshot-1.png) | ![](docs/screenshot-2.png) | ![](docs/screenshot-3.png) |

### Controls

| Action | Input |
|---|---|
| Move building (merge direction) | WASD / Arrow keys |
| Construct a building | Spacebar |
| Toggle inspection mode | INFORMATION button |
| Build a new building | BUILD button |
| Expand the land | EXPAND button |
| Advance to next age | NEXT AGE button |
| Inspect / sell building | Click a building in inspection mode |

## Download

[![Available on itch.io](https://jessemillar.github.io/available-on-itchio-badge/badge-color.png)](https://umutcanekinci.itch.io/highrise)

Grab a ready-to-play build for your OS from [itch.io](https://umutcanekinci.itch.io/highrise) or the [latest GitHub release](https://github.com/umutcanekinci/highrise/releases/latest) — no Python required. Unzip and run:

| OS | Run |
|----|-----|
| Windows | Extract `highrise-windows.zip`, run `highrise.exe` |
| macOS | Extract `highrise-macos.zip`, open `Highrise.app` |
| Linux | Extract `highrise-linux.zip`, run `./highrise/highrise` |

> macOS Gatekeeper: the app is unsigned, so the first launch needs **right-click → Open** (or `xattr -dr com.apple.quarantine Highrise.app`).

## Requirements (from source)

- Python 3.12+
- [pygame-ce](https://github.com/pygame-community/pygame-ce), pyyaml (resolved automatically from `pyproject.toml` / `uv.lock`)
- [uv](https://docs.astral.sh/uv/) (optional but recommended)

## Running

```bash
git clone --recurse-submodules https://github.com/umutcanekinci/highrise.git
cd highrise
uv sync
uv run python __main__.py
```

If you forgot `--recurse-submodules`: `git submodule update --init`.

Without `uv`: `pip install .` then `python __main__.py`.

## Building a standalone bundle

Builds are produced by [PyInstaller](https://pyinstaller.org/) from `highrise.spec`, which bundles `assets/` and `config/` alongside the executable (onedir). To build locally for your current OS:

```bash
uv sync --group build
uv run pyinstaller highrise.spec --noconfirm
```

The result lands in `dist/highrise/` (`dist/Highrise.app` on macOS).

### Cutting a release

Per-OS bundles for Windows, macOS, and Linux are built and published automatically by [`.github/workflows/release.yml`](.github/workflows/release.yml) when a version tag is pushed:

```bash
git tag v0.1.0
git push origin v0.1.0
```

The workflow builds on each OS, zips the bundle, attaches all three to a GitHub Release (with auto-generated notes), and pushes each build to its [itch.io](https://umutcanekinci.itch.io/highrise) channel via [Butler](https://itch.io/docs/butler/). Use the workflow's **Run workflow** button to test a build without publishing.

## Project layout

```
__main__.py            Entry point — injects src/ + src/pygame_core/ into sys.path
src/app/game.py        Game class — wires Application + Events + Persistence mixins
src/domain/            Pure data (Player)
src/gameplay/          Tilemap, tile selector, buildings, clouds
src/ui/                Info panel and UI helpers
src/pygame_core/       Engine submodule (Application, PanelLoaderExt, Database, ...)
config/                YAML: assets, panels, settings
databases/             SQLite save file (auto-created on first run)
assets/                Images, sounds, fonts
```

See [CLAUDE.md](CLAUDE.md) for the full architecture overview.

## Credits

Art and UI from [Kenney](https://www.kenney.nl/) — [Hexagon Buildings](https://www.kenney.nl/assets/hexagon-buildings) and [UI Pack](https://www.kenney.nl/assets/ui-pack).

## Contributing

1. Fork this repository.
2. Clone your fork: `git clone --recurse-submodules https://github.com/<you>/highrise.git`
3. Create a branch: `git checkout -b feature/<your-feature>`
4. Commit + push: `git commit -am "<message>" && git push origin feature/<your-feature>`
5. Open a pull request.

## Author

Umutcan Ekinci — [umutcannekinci@gmail.com](mailto:umutcannekinci@gmail.com)

See also the [contributors](https://github.com/umutcanekinci/highrise/contributors).

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file.
