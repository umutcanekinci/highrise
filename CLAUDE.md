# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Game

```bash
# Install dependencies (resolved from pyproject.toml / uv.lock)
uv sync             # preferred — installs the locked dep set
# or for users without uv:
pip install .       # installs pygame-ce + pyyaml from pyproject.toml

# Run the game (__main__.py adds src/ and src/pygamine/ to sys.path)
python __main__.py
```

## Testing

```bash
uv run --group dev pytest tests/ -q                      # this app's own logic tests
uv run --group dev pytest tests/ --cov --cov-report=term  # with coverage
```

No lint configuration in this project. Note: several paths in this file (`src/game.py`,
`src/game_events.py`, `src/game_audio.py`, `src/building.py`, `src/cloud.py`, `src/tile.py`,
`src/ext/guiobject.py`) are stale — the actual layout has since moved to `src/app/`,
`src/domain/`, `src/gameplay/{buildings,clouds,tiles}/`, and `src/ui/` (see the test suite's
imports for the current module paths).

## Architecture Overview

### Entry Point and Game Class

`__main__.py` calls `Game().run()`. `src/game.py` defines the `Game` class, which inherits from `pygamine.Application` and three mixins: `GameEventsMixin` (`src/game_events.py`), `GamePersistenceMixin` (`src/game_persistence.py`), and `GameAudioMixin` (`src/game_audio.py`). These mixins handle event routing, SQLite save/load, and sound management respectively.

### pygamine — Shared Utility Package

`src/pygamine/` is a standalone, editable-installed package shared across multiple game projects. It provides:
- `Application` — base game loop class
- `AssetManager` + `ImagePath`/`FontPath`/`SoundPath` — asset loading/caching
- `PanelManager` + `PanelLoaderExt` — screen/panel management driven by `config/panels.yaml`
- `GameObject` / component system (`Transform`, `Rigidbody2D`, `SpriteRenderer2D`) — Unity-style entity model
- `Database` — SQLite wrapper (saves to `databases/database.db`)
- `MouseInteractive` mixin — mouse input for game objects

**Changes to `src/pygamine/` affect all games that depend on it.**

### Entity Hierarchy

```
pygamine.GameObject
├── StateObject (src/state_object.py) + MouseInteractive
│   ├── Building  (src/building.py)
│   └── Cloud     (src/cloud.py)
└── TextObject, InputBox  (pygamine ui_widgets)

GuiObject (src/ext/guiobject.py) — extends StateObject for UI elements
Button, ButtonText (src/button.py) — extend GuiObject
```

### YAML-Driven UI

All UI panels, buttons, and layout are declared in `config/panels.yaml`. Python code never hard-codes widget positions or sizes for UI — use `PanelLoaderExt` and `panel_factory.py` to wire YAML definitions to Python objects. `config/assets.yaml` declares the asset manifest (fonts, images by category).

### Isometric Tilemap

`src/tile.py` renders an isometric diamond grid. Tile selection uses point-in-quadrangle collision. Selected tiles visually shift up by 10 px. Building movement (WASD/arrows) triggers 2048-style merge logic: same-level adjacent buildings merge and level up.

### Persistence

SQLite database at `databases/database.db`. Two tables: `game` (age, map size, money, volumes) and `buildings` (level, row, column). The database auto-initializes on first run. Save/load logic lives entirely in `GamePersistenceMixin`.

### Audio

Two mixer channels: channel 0 for looping music, channel 1 for SFX. Volumes are stored in the database and applied on load. All audio logic is in `GameAudioMixin`.