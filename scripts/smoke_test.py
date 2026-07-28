"""Headless boot check -- catches config/panel wiring mistakes that only
surface once objects are actually built (e.g. a panels.yaml entry missing a
required key). Run locally with:

    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run python scripts/smoke_test.py

Requires cwd = repo root (matches how __main__.py and CI both invoke it).
Read-only with respect to databases/database.db: load_data() only inserts a
fresh row when the table is empty and never calls save_game()/delete_data(),
so an existing save is left untouched.
"""
import sys
from pathlib import Path

import yaml

sys.path.insert(0, "src")
sys.path.insert(0, "src/pygamine")

PANELS = (
    "menu", "play", "settings",
    "display_settings", "audio_settings", "game_settings",
    "developer", "game",
)


def check_config_yaml() -> None:
    for path in sorted(Path("config").glob("*.yaml")):
        yaml.safe_load(path.read_text(encoding="utf-8"))
        print(f"  {path}: OK")


def boot_game() -> None:
    from app.game import Game

    game = Game()
    # Mirrors Game.run() up to (not including) the blocking super().run()
    # loop and the splash screen / background music, which don't apply
    # headlessly.
    game.load_data()
    game.tile_selector.tilemap = game.tilemap
    game.add_objects()
    game.set_age(game.buildings.age_number)
    game.update_button_texts()
    game.open_panel("menu")
    game.info_panel.close()

    for panel in PANELS:
        game.open_panel(panel)
        game.update()
        game.draw()
        print(f"  {panel}: OK")


def main() -> None:
    print("Validating config/*.yaml...")
    check_config_yaml()
    print("Booting Game() and rendering every panel...")
    boot_game()
    print("Smoke test passed.")


if __name__ == "__main__":
    main()
