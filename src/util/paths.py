"""Filesystem anchors that work both from source and inside a PyInstaller bundle.

The game loads `assets/` and `config/` with paths relative to the current
working directory (e.g. ``game.py`` opens ``"config/assets.yaml"``). That only
holds when the process runs from the project root.

When PyInstaller freezes the app, data files bundled via the spec's ``datas``
are unpacked next to the executable (onedir) or extracted to a temp dir
(onefile); either way their location is exposed as ``sys._MEIPASS``. To keep
the existing relative paths valid in both modes, ``__main__`` chdirs into
:func:`resource_root` at startup.
"""

from __future__ import annotations

import sys
from pathlib import Path


def resource_root() -> Path:
    """Directory that contains the bundled ``assets/`` and ``config/`` trees.

    Frozen: the PyInstaller extraction dir. From source: the repo root
    (``src/util/paths.py`` -> two levels up).
    """
    bundle = getattr(sys, "_MEIPASS", None)
    if bundle is not None:
        return Path(bundle)
    return Path(__file__).resolve().parents[2]
