"""GameEventsMixin -- FakeGame subclasses the mixin directly (same approach
as chokepoint's test_game_events.py) so intra-mixin calls (_activate, used
by nearly every handler) resolve normally. Methods GameEventsMixin expects
from Game/GamePersistenceMixin/Application are stubbed and logged to
`self.calls` so a test can assert what got invoked without constructing a
real Game() (which needs the full YAML panel/asset stack for no benefit)."""

from types import SimpleNamespace

import pygame
import pytest

from app.game_events import GameEventsMixin


class FakeButton:
    def __init__(self, clicked=False, focused=False):
        self.clicked = clicked
        self.focused = focused
        self.base_state = None

    def is_clicked(self, event, mouse_pos) -> bool:
        return self.clicked

    def set_base_state(self, state) -> None:
        self.base_state = state


class FakeGuiObject:
    """Stand-in for the "info_panel" widget specifically -- a plain active
    flag, distinct from FakeInfoPanel (the InfoPanel wrapper `self.info_panel`
    reparents onto), matching how handle_game_events reads panel["info_panel"].active."""

    def __init__(self, active=False):
        self.active = active


class FakeAudio:
    def __init__(self, music=0.5, sfx=0.5):
        self._music = music
        self._sfx = sfx
        self.played = []

    def music_volume(self) -> float:
        return self._music

    def sfx_volume(self) -> float:
        return self._sfx

    def set_music_volume(self, value) -> None:
        self._music = value

    def set_sfx_volume(self, value) -> None:
        self._sfx = value

    def play_sfx(self, path) -> None:
        self.played.append(path)


class FakeTileSelector:
    def __init__(self, selected_building=None):
        self.is_active = False
        self.update_calls = 0
        self._selected_building = selected_building

    def update_selection(self) -> None:
        self.update_calls += 1

    def get_selected_building(self):
        return self._selected_building


class FakeInfoPanel:
    def __init__(self):
        self.building = None
        self.opened = False
        self.close_calls = 0

    def refresh(self, building) -> None:
        self.building = building

    def open(self) -> None:
        self.opened = True

    def close(self) -> None:
        self.opened = False
        self.close_calls += 1


class FakePanelManager(dict):
    pass


def make_panels():
    return FakePanelManager({
        "menu": {
            "play_button": FakeButton(), "settings_button": FakeButton(),
            "developer_button": FakeButton(), "exit_button": FakeButton(),
        },
        "play": {
            "new_game_button": FakeButton(), "continue_button": FakeButton(),
            "play_back_button": FakeButton(),
        },
        "settings": {
            "display_settings_button": FakeButton(), "audio_settings_button": FakeButton(),
            "game_settings_button": FakeButton(), "settings_back_button": FakeButton(),
        },
        "display_settings": {
            "window_mode_minus_button": FakeButton(), "window_mode_plus_button": FakeButton(),
            "window_size_minus_button": FakeButton(), "window_size_plus_button": FakeButton(),
            "display_back_button": FakeButton(),
        },
        "audio_settings": {
            "music_volume_plus_button": FakeButton(), "music_volume_minus_button": FakeButton(),
            "sfx_volume_plus_button": FakeButton(), "sfx_volume_minus_button": FakeButton(),
            "cancel_button": FakeButton(), "save_button": FakeButton(),
        },
        "game_settings": {"game_settings_back_button": FakeButton()},
        "developer": {
            "github_button": FakeButton(), "linkedin_button": FakeButton(),
            "developer_back_button": FakeButton(),
        },
        "game": {
            "info_panel": FakeGuiObject(active=False),
            "sell_button": FakeButton(), "close_button": FakeButton(),
            "selection_mode_button": FakeButton(),
            "expand_button": FakeButton(), "build_button": FakeButton(),
            "next_age_button": FakeButton(),
        },
    })


class FakeGame(GameEventsMixin):
    def __init__(self):
        self.panel_manager = make_panels()
        self.mouse = SimpleNamespace(position=(0, 0))
        self.audio = FakeAudio()
        self.click_sound_path = "assets/sfx/click.ogg"
        self.old_music_volume = 0.5
        self.old_sfx_volume = 0.5
        self.tile_selector = FakeTileSelector()
        self.info_panel = FakeInfoPanel()
        self.buildings = SimpleNamespace(remove=lambda b: self.calls.append(("remove", b)))
        self.player = SimpleNamespace(earn=lambda a: self.calls.append(("earn", a)))
        self.calls: list = []

    def play(self):                       self.calls.append("play")
    def new_game(self):                   self.calls.append("new_game")
    def open_panel(self, tab):            self.calls.append(("open_panel", tab))
    def cycle_window_mode(self, step):    self.calls.append(("cycle_window_mode", step))
    def cycle_resolution(self, step):     self.calls.append(("cycle_resolution", step))
    def set_window_mode_label(self):      self.calls.append("set_window_mode_label")
    def set_window_size_label(self):      self.calls.append("set_window_size_label")
    def set_music_label(self, v):         self.calls.append(("set_music_label", v))
    def set_sfx_label(self, v):           self.calls.append(("set_sfx_label", v))
    def save_audio_settings(self):        self.calls.append("save_audio_settings")
    def expand(self):                     self.calls.append("expand")
    def create_building(self):            self.calls.append("create_building")
    def next_age(self):                   self.calls.append("next_age")
    def move_buildings(self, rotation):   self.calls.append(("move_buildings", rotation))
    def update_button_texts(self):        self.calls.append("update_button_texts")


def click_up():
    return pygame.event.Event(pygame.MOUSEBUTTONUP, button=1)


# ── _activate ────────────────────────────────────────────────────────────────

def test_activate_true_on_click_plays_the_click_sound():
    game = FakeGame()
    button = FakeButton(clicked=True)

    assert game._activate(button, click_up()) is True
    assert game.audio.played == [game.click_sound_path]


# ── menu ─────────────────────────────────────────────────────────────────────

def test_menu_play_button_calls_play():
    game = FakeGame()
    game.panel_manager["menu"]["play_button"].clicked = True

    game.handle_menu_events(click_up())

    assert "play" in game.calls


def test_menu_navigation_buttons():
    for button_name, dest in (
        ("settings_button", "settings"), ("developer_button", "developer"), ("exit_button", "exit"),
    ):
        game = FakeGame()
        game.panel_manager["menu"][button_name].clicked = True
        game.handle_menu_events(click_up())
        assert ("open_panel", dest) in game.calls


# ── play ─────────────────────────────────────────────────────────────────────

def test_play_panel_buttons():
    game = FakeGame()
    game.panel_manager["play"]["new_game_button"].clicked = True
    game.handle_play_events(click_up())
    assert "new_game" in game.calls

    game2 = FakeGame()
    game2.panel_manager["play"]["continue_button"].clicked = True
    game2.handle_play_events(click_up())
    assert ("open_panel", "game") in game2.calls

    game3 = FakeGame()
    game3.panel_manager["play"]["play_back_button"].clicked = True
    game3.handle_play_events(click_up())
    assert ("open_panel", "menu") in game3.calls


# ── settings ─────────────────────────────────────────────────────────────────

def test_settings_navigation():
    for button_name, dest in (
        ("display_settings_button", "display_settings"),
        ("game_settings_button", "game_settings"),
        ("settings_back_button", "menu"),
    ):
        game = FakeGame()
        game.panel_manager["settings"][button_name].clicked = True
        game.handle_settings_events(click_up())
        assert ("open_panel", dest) in game.calls


def test_settings_audio_settings_button_snapshots_the_current_volumes():
    game = FakeGame()
    game.audio._music, game.audio._sfx = 0.7, 0.3
    game.old_music_volume, game.old_sfx_volume = 0.0, 0.0
    game.panel_manager["settings"]["audio_settings_button"].clicked = True

    game.handle_settings_events(click_up())

    assert (game.old_music_volume, game.old_sfx_volume) == (0.7, 0.3)
    assert ("open_panel", "audio_settings") in game.calls


# ── display settings ─────────────────────────────────────────────────────────

def test_display_settings_window_mode_buttons():
    game = FakeGame()
    game.panel_manager["display_settings"]["window_mode_minus_button"].clicked = True
    game.handle_display_settings_events(click_up())
    assert ("cycle_window_mode", -1) in game.calls
    assert "set_window_mode_label" in game.calls
    assert "set_window_size_label" in game.calls

    game2 = FakeGame()
    game2.panel_manager["display_settings"]["window_mode_plus_button"].clicked = True
    game2.handle_display_settings_events(click_up())
    assert ("cycle_window_mode", 1) in game2.calls


def test_display_settings_window_size_buttons():
    game = FakeGame()
    game.panel_manager["display_settings"]["window_size_minus_button"].clicked = True
    game.handle_display_settings_events(click_up())
    assert ("cycle_resolution", -1) in game.calls
    assert "set_window_size_label" in game.calls

    game2 = FakeGame()
    game2.panel_manager["display_settings"]["window_size_plus_button"].clicked = True
    game2.handle_display_settings_events(click_up())
    assert ("cycle_resolution", 1) in game2.calls


def test_display_settings_back_button():
    game = FakeGame()
    game.panel_manager["display_settings"]["display_back_button"].clicked = True

    game.handle_display_settings_events(click_up())

    assert ("open_panel", "settings") in game.calls


# ── audio settings ───────────────────────────────────────────────────────────

def test_audio_settings_volume_buttons_adjust_by_a_tenth():
    game = FakeGame()
    game.audio._music = 0.5
    game.panel_manager["audio_settings"]["music_volume_plus_button"].clicked = True
    game.handle_audio_settings_events(click_up())
    assert game.audio._music == pytest.approx(0.6)
    assert ("set_music_label", pytest.approx(0.6)) in game.calls

    game2 = FakeGame()
    game2.audio._sfx = 0.5
    game2.panel_manager["audio_settings"]["sfx_volume_minus_button"].clicked = True
    game2.handle_audio_settings_events(click_up())
    assert game2.audio._sfx == pytest.approx(0.4)


def test_audio_settings_cancel_restores_the_snapshotted_volumes():
    game = FakeGame()
    game.audio._music, game.audio._sfx = 0.9, 0.9
    game.old_music_volume, game.old_sfx_volume = 0.2, 0.3
    game.panel_manager["audio_settings"]["cancel_button"].clicked = True

    game.handle_audio_settings_events(click_up())

    assert (game.audio._music, game.audio._sfx) == (0.2, 0.3)
    assert ("open_panel", "settings") in game.calls


def test_audio_settings_save_persists_and_returns_to_settings():
    game = FakeGame()
    game.panel_manager["audio_settings"]["save_button"].clicked = True

    game.handle_audio_settings_events(click_up())

    assert "save_audio_settings" in game.calls
    assert ("open_panel", "settings") in game.calls


# ── game settings / developer ────────────────────────────────────────────────

def test_game_settings_back_button():
    game = FakeGame()
    game.panel_manager["game_settings"]["game_settings_back_button"].clicked = True

    game.handle_game_settings_events(click_up())

    assert ("open_panel", "settings") in game.calls


def test_developer_links_open_in_a_browser(monkeypatch):
    import app.game_events as game_events_module
    opened = []
    monkeypatch.setattr(game_events_module.webbrowser, "open", lambda url: opened.append(url))

    game = FakeGame()
    game.panel_manager["developer"]["github_button"].clicked = True
    game.handle_developer_events(click_up())
    assert opened == ["https://www.github.com/umutcanekinci/"]

    game2 = FakeGame()
    game2.panel_manager["developer"]["linkedin_button"].clicked = True
    game2.handle_developer_events(click_up())
    assert opened == ["https://www.github.com/umutcanekinci/", "https://www.linkedin.com/in/umutcanekinci/"]


def test_developer_back_button():
    game = FakeGame()
    game.panel_manager["developer"]["developer_back_button"].clicked = True

    game.handle_developer_events(click_up())

    assert ("open_panel", "menu") in game.calls


# ── game panel ───────────────────────────────────────────────────────────────

def test_game_events_updates_selection_while_the_selector_is_active():
    game = FakeGame()
    game.tile_selector.is_active = True

    game.handle_game_events(pygame.event.Event(pygame.MOUSEMOTION, pos=(0, 0)))

    assert game.tile_selector.update_calls == 1


def test_game_events_info_panel_open_sell_button_sells_the_building():
    game = FakeGame()
    game.panel_manager["game"]["info_panel"].active = True
    game.info_panel.building = SimpleNamespace(sell_price=42)
    game.panel_manager["game"]["sell_button"].clicked = True

    game.handle_game_events(click_up())

    assert ("remove", game.info_panel.building) in game.calls
    assert ("earn", 42) in game.calls
    assert game.info_panel.close_calls == 1
    assert "update_button_texts" in game.calls


def test_game_events_info_panel_open_close_button_just_closes_it():
    game = FakeGame()
    game.panel_manager["game"]["info_panel"].active = True
    game.panel_manager["game"]["close_button"].clicked = True

    game.handle_game_events(click_up())

    assert game.info_panel.close_calls == 1
    assert not any(c[0] == "remove" for c in game.calls if isinstance(c, tuple))


def test_game_events_info_panel_open_ignores_expand_build_and_hotkeys():
    game = FakeGame()
    game.panel_manager["game"]["info_panel"].active = True
    game.panel_manager["game"]["expand_button"].clicked = True  # should be ignored -- info panel owns input

    game.handle_game_events(click_up())

    assert "expand" not in game.calls


def test_game_events_selection_mode_button_toggles_tile_selector():
    game = FakeGame()
    game.panel_manager["game"]["selection_mode_button"].clicked = True

    game.handle_game_events(click_up())

    assert game.tile_selector.is_active is True
    assert game.panel_manager["game"]["selection_mode_button"].base_state == "on"

    game.panel_manager["game"]["selection_mode_button"].clicked = True
    game.handle_game_events(click_up())

    assert game.tile_selector.is_active is False
    assert game.panel_manager["game"]["selection_mode_button"].base_state == "off"


def test_game_events_clicking_a_selected_building_opens_the_info_panel():
    game = FakeGame()
    game.tile_selector.is_active = True
    building = SimpleNamespace(name="tower")
    game.tile_selector._selected_building = building

    game.handle_game_events(click_up())

    assert game.info_panel.building is building
    assert game.info_panel.opened is True
    assert game.audio.played == [str(game.click_sound_path)]


def test_game_events_expand_build_and_next_age_buttons():
    game = FakeGame()
    game.panel_manager["game"]["expand_button"].clicked = True
    game.handle_game_events(click_up())
    assert "expand" in game.calls

    game2 = FakeGame()
    game2.panel_manager["game"]["build_button"].clicked = True
    game2.handle_game_events(click_up())
    assert "create_building" in game2.calls

    game3 = FakeGame()
    game3.panel_manager["game"]["next_age_button"].clicked = True
    game3.handle_game_events(click_up())
    assert "next_age" in game3.calls


def test_game_events_keyboard_shortcuts():
    cases = [
        (pygame.K_SPACE, "create_building"),
        (pygame.K_RIGHT, ("move_buildings", "right")),
        (pygame.K_d, ("move_buildings", "right")),
        (pygame.K_LEFT, ("move_buildings", "left")),
        (pygame.K_a, ("move_buildings", "left")),
        (pygame.K_UP, ("move_buildings", "up")),
        (pygame.K_w, ("move_buildings", "up")),
        (pygame.K_DOWN, ("move_buildings", "down")),
        (pygame.K_s, ("move_buildings", "down")),
    ]
    for key, expected in cases:
        game = FakeGame()
        game.handle_game_events(pygame.event.Event(pygame.KEYUP, key=key))
        assert expected in game.calls
