"""Filesystem anchors that work both from source and inside a PyInstaller bundle.

The game loads `assets/` and `config/` with paths relative to the current
working directory (e.g. ``game.py`` opens ``"config/assets.yaml"``). That only
holds when the process runs from the project root.

When PyInstaller freezes the app, data files bundled via the spec's ``datas``
are unpacked next to the executable (onedir) or extracted to a temp dir
(onefile); either way their location is exposed as ``sys._MEIPASS``. To keep
the existing relative paths valid in both modes, ``__main__`` chdirs into
:func:`resource_root` at startup.

Implementation lives in ``pygamine.paths`` -- shared with every sibling
project, since the logic has nothing project-specific in it. Re-exported
here so existing ``from util.paths import resource_root`` call sites don't
need to change.
"""

from __future__ import annotations

from pygamine.paths import resource_root as resource_root, resource_path as resource_path
