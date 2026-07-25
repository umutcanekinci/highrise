"""Shared pytest setup and fixtures for highrise's app-level test suite.

Run from the repo root (`uv run pytest`, matching how __main__.py assumes
cwd == repo root for its own "config/..."-relative paths).
"""

import os

# Dummy SDL drivers so pygame can run headless (e.g. in CI) without opening a
# real window or probing for a sound device. Must be set before pygame is
# imported anywhere.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from pygame_core.asset_manager import AssetManager

pygame.init()
# Tile/Building load images via convert_alpha(), which raises without a
# display surface. Application.__init__ normally provides one via
# set_resolution(); these tests construct game objects directly, with no
# Application/Game involved, so they need their own.
pygame.display.set_mode((1, 1))


@pytest.fixture(scope="session")
def assets() -> AssetManager:
    manager = AssetManager()
    manager.load_manifest("config/assets.yaml")
    missing = manager.validate()
    assert not missing, f"Missing assets: {missing}"
    return manager
