#!/usr/bin/env python3
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT / "src" / "pygame_core"))

# Anchor all cwd-relative asset/config paths to the resource root so the game
# works both from source and from a PyInstaller bundle (see util.paths).
from util.paths import resource_root

os.chdir(resource_root())

from app.game import Game

if __name__ == "__main__":
    Game().run()
