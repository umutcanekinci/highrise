"""Game itself (app/game.py) -- constructing a real Game() needs the full
YAML panel/asset/tilemap stack for no benefit here (same reasoning
test_game_events.py/test_game_persistence.py already established for their
mixins). These build a bare Game instance via object.__new__(Game), which
skips __init__ entirely, then attach only what the method under test
touches -- real Player/Buildings/Tilemap where the game logic itself is
under test, small fakes for pure UI/plumbing (panel_manager, audio, ...).
"""
from types import SimpleNamespace

import pygame
import pytest

from app.game import Game
from domain.player import Player
from gameplay.buildings.building import Building, Buildings
from gameplay.tilemap import Tilemap

MAX_SIZE = 7
MAX_BUILDING_LEVEL = 10


class Spy:
    def __init__(self):
        self.calls = []

    def __call__(self, *args):
        self.calls.append(args)


class FakeText:
    def __init__(self):
        self.text = None
        self.state = None

    def set_text(self, text, state=None) -> None:
        self.text = text
        self.state = state


class FakePanelManager(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_panel = "menu"

    def keys(self):
        return dict.keys(self)

    def update(self):
        pass

    def draw(self, surface):
        pass

    def handle_event(self, event, pos):
        pass

    def open_panel(self, tab):
        self.current_panel = tab


class FakeAudio:
    def __init__(self):
        self.played = []
        self._music = 0.5
        self._sfx = 0.5

    def play_sfx(self, path):
        self.played.append(path)

    def music_volume(self):
        return self._music

    def sfx_volume(self):
        return self._sfx

    def set_music_volume(self, v):
        self._music = v

    def set_sfx_volume(self, v):
        self._sfx = v


def make_panels():
    panel = FakePanelManager({
        "game": {"build_button_text": FakeText()},
        "audio_settings": {"music_volume_entry_text": FakeText(), "sfx_volume_entry_text": FakeText()},
        "display_settings": {"window_size_entry_text": FakeText(), "window_mode_entry_text": FakeText()},
    })
    return panel


def make_game(assets, *, size=3, max_size=MAX_SIZE, starting_money=500):
    game = object.__new__(Game)
    game.assets = assets
    game.player = Player()
    game.player.money = starting_money
    game.buildings = Buildings(assets)
    game.tilemap = Tilemap(size, max_size)
    game.max_size = max_size
    game.max_building_level = MAX_BUILDING_LEVEL
    game.starting_money = starting_money
    game.tile_selector = SimpleNamespace(is_active=False, tilemap=game.tilemap)
    game.audio = FakeAudio()
    game.click_sound_path = "assets/sfx/click.ogg"
    game.go_back_sound_path = "assets/sfx/back.ogg"
    game.panel_manager = make_panels()
    game.cloud_animation = SimpleNamespace(create_clouds=Spy(), update=Spy(), draw=Spy())
    game.info_panel = SimpleNamespace(is_active=False, close=Spy())
    game.old_music_volume = 0.5
    game.old_sfx_volume = 0.5
    game.update_button_texts = Spy()
    return game


# ── expand ───────────────────────────────────────────────────────────────────

def test_expand_grows_the_map_and_relocates_building_tiles(assets):
    game = make_game(assets, size=3, starting_money=100_000)
    tile = game.tilemap[1][1]
    building = Building(1, 0, tile)
    game.buildings.append(building)

    game.expand()

    assert (game.tilemap.row_count, game.tilemap.column_count) == (4, 4)
    # Same logical (row, col) on the new, bigger grid -- a fresh Tile object.
    assert building.tile is game.tilemap[1][1]
    assert len(game.update_button_texts.calls) == 1
    assert game.audio.played == [game.click_sound_path]


def test_expand_does_nothing_at_max_size(assets):
    game = make_game(assets, size=MAX_SIZE, starting_money=100_000)

    game.expand()

    assert (game.tilemap.row_count, game.tilemap.column_count) == (MAX_SIZE, MAX_SIZE)
    assert game.audio.played == []


def test_expand_does_nothing_when_unaffordable(assets):
    game = make_game(assets, size=3, starting_money=0)

    game.expand()

    assert (game.tilemap.row_count, game.tilemap.column_count) == (3, 3)
    assert game.player.money == 0


# ── add_building ─────────────────────────────────────────────────────────────

def test_add_building_appends_and_sorts_by_column(assets):
    game = make_game(assets, size=3)

    game.add_building(1, 1, 3)
    game.add_building(2, 1, 1)

    assert [b.tile.column_number for b in game.buildings] == [1, 3]


def test_add_building_marks_tiles_full_once_the_grid_is_saturated(assets):
    game = make_game(assets, size=1)  # a single tile

    game.add_building(1, 1, 1)

    assert game.panel_manager["game"]["build_button_text"].text == "TILES FULL"


# ── create_building ──────────────────────────────────────────────────────────

def test_create_building_places_on_an_empty_tile_and_spends_money(assets, monkeypatch):
    game = make_game(assets, size=2, starting_money=100_000)
    monkeypatch.setattr("app.game.choice", lambda seq: sorted(seq)[0])

    game.create_building()

    assert len(game.buildings) == 1
    assert game.buildings[0].tile.row_number, game.buildings[0].tile.column_number == (1, 1)
    assert game.player.money == 100_000 - game.buildings.get_build_cost()
    assert game.audio.played == [game.click_sound_path]


def test_create_building_does_nothing_when_unaffordable(assets):
    game = make_game(assets, size=2, starting_money=0)

    game.create_building()

    assert len(game.buildings) == 0


def test_create_building_does_nothing_while_buildings_are_moving(assets, monkeypatch):
    game = make_game(assets, size=2, starting_money=100_000)
    monkeypatch.setattr(type(game.buildings), "is_moving", lambda self: True, raising=False)

    game.create_building()

    assert len(game.buildings) == 0


# ── age progression ──────────────────────────────────────────────────────────

def test_set_age_within_range_updates_buildings_and_button_texts(assets):
    game = make_game(assets, size=3)

    game.set_age(1)

    assert game.buildings.age_number == 1
    assert len(game.update_button_texts.calls) == 1


def test_set_age_beyond_max_is_a_no_op(assets):
    game = make_game(assets, size=3)
    beyond_max = game.buildings.max_age_number + 1

    game.set_age(beyond_max)

    assert game.buildings.age_number == 0


def test_next_age_advances_and_spends_money(assets):
    game = make_game(assets, size=3, starting_money=100_000)

    game.next_age()

    assert game.buildings.age_number == 1
    assert game.audio.played == [game.click_sound_path]


def test_next_age_does_nothing_when_unaffordable(assets):
    game = make_game(assets, size=3, starting_money=0)

    game.next_age()

    assert game.buildings.age_number == 0


def test_next_age_does_nothing_at_max_age(assets):
    game = make_game(assets, size=3, starting_money=100_000_000)
    game.buildings.age_number = game.buildings.max_age_number

    game.next_age()

    assert game.buildings.age_number == game.buildings.max_age_number


# ── move_buildings ───────────────────────────────────────────────────────────

def test_move_buildings_forwards_to_buildings_move(assets):
    game = make_game(assets, size=3)
    game.buildings.move = Spy()

    game.move_buildings("right")

    assert game.buildings.move.calls == [("right", game.tilemap, MAX_BUILDING_LEVEL)]


def test_move_buildings_is_a_no_op_while_the_tile_selector_is_active(assets):
    game = make_game(assets, size=3)
    game.tile_selector.is_active = True
    game.buildings.move = Spy()

    game.move_buildings("right")

    assert game.buildings.move.calls == []


# ── payouts / panels ─────────────────────────────────────────────────────────

def test_on_building_payout_credits_the_player(assets):
    game = make_game(assets, size=3)

    game._on_building_payout(15)

    assert game.player.money == 500 + 15


def test_open_panel_exits_for_the_exit_tab(assets):
    game = make_game(assets, size=3)
    game.exit = Spy()

    game.open_panel("exit")

    assert len(game.exit.calls) == 1
    assert len(game.cloud_animation.create_clouds.calls) == 0


def test_open_panel_switches_tabs_and_spawns_clouds(assets):
    game = make_game(assets, size=3)

    game.open_panel("game")

    assert game.panel_manager.current_panel == "game"
    assert len(game.cloud_animation.create_clouds.calls) == 1


def test_has_save_data_true_with_buildings_or_advanced_age(assets):
    game = make_game(assets, size=3)
    assert game.has_save_data() is False

    game.buildings.append(Building(1, 0, game.tilemap[0][0]))
    assert game.has_save_data() is True

    game2 = make_game(assets, size=3)
    game2.buildings.age_number = 1
    assert game2.has_save_data() is True


def test_play_opens_the_play_panel_when_a_save_exists(assets):
    game = make_game(assets, size=3)
    game.buildings.append(Building(1, 0, game.tilemap[0][0]))

    game.play()

    assert game.panel_manager.current_panel == "play"


def test_play_starts_a_new_game_with_no_save(assets):
    game = make_game(assets, size=3)
    game.delete_data = Spy()
    game.load_data = Spy()
    game.add_objects = Spy()
    game.set_music_label = Spy()
    game.set_sfx_label = Spy()

    game.play()

    assert len(game.load_data.calls) == 1
    assert game.panel_manager.current_panel == "game"


# ── volume / window labels ───────────────────────────────────────────────────

def test_set_music_and_sfx_labels_round_to_a_percentage(assets):
    game = make_game(assets, size=3)

    game.set_music_label(0.567)
    game.set_sfx_label(1.0)

    assert game.panel_manager["audio_settings"]["music_volume_entry_text"].text == "%57"
    assert game.panel_manager["audio_settings"]["sfx_volume_entry_text"].text == "%100"


def test_set_music_label_clamps_out_of_range_values(assets):
    game = make_game(assets, size=3)

    game.set_music_label(-0.5)
    assert game.panel_manager["audio_settings"]["music_volume_entry_text"].text == "%0"

    game.set_music_label(1.5)
    assert game.panel_manager["audio_settings"]["music_volume_entry_text"].text == "%100"


def test_set_window_size_and_mode_labels(assets):
    game = make_game(assets, size=3)
    game._resolution_override = (1280, 720)  # `resolution` itself is read-only
    game._window_mode = "windowed"

    game.set_window_size_label()
    game.set_window_mode_label()

    assert game.panel_manager["display_settings"]["window_size_entry_text"].text == "1280x720"
    assert game.panel_manager["display_settings"]["window_mode_entry_text"].text == "WINDOWED"


# ── event / update / draw dispatch ───────────────────────────────────────────

def test_handle_event_dispatches_to_the_current_panels_handler(assets):
    game = make_game(assets, size=3)
    game.panel_manager.current_panel = "game"
    game.mouse = SimpleNamespace(position=(0, 0))
    game.menu_controllers = {}
    handler = Spy()
    game.handlers = {"game": handler}
    event = pygame.event.Event(pygame.MOUSEMOTION, pos=(0, 0))

    game.handle_event(event)

    assert handler.calls == [(event,)]


def test_update_assigns_a_payout_callback_to_buildings_missing_one(assets):
    game = make_game(assets, size=3)
    game.panel_manager.update = Spy()
    building = Building(1, 0, game.tilemap[0][0])
    game.buildings.append(building)
    game.buildings.update = Spy()

    game.update()

    # Bound-method identity isn't stable across separate attribute accesses
    # in Python -- == (same underlying function + instance) is the right check.
    assert building.on_payout == game._on_building_payout


def test_draw_calls_panels_and_clouds(assets):
    game = make_game(assets, size=3)
    game.panel_manager.draw = Spy()
    game.window = pygame.Surface((100, 100))

    game.draw()

    assert len(game.panel_manager.draw.calls) == 1
    assert len(game.cloud_animation.draw.calls) == 1


# ── exit flow ────────────────────────────────────────────────────────────────

def test_on_exit_request_from_menu_exits(assets):
    game = make_game(assets, size=3)
    game.panel_manager.current_panel = "menu"
    game.exit = Spy()

    game.on_exit_request()

    assert len(game.exit.calls) == 1
    assert game.audio.played == [game.go_back_sound_path]


@pytest.mark.parametrize("panel,expected", [
    ("play", "menu"), ("settings", "menu"),
    ("display_settings", "settings"), ("game_settings", "settings"),
    ("developer", "menu"),
])
def test_on_exit_request_navigates_back(assets, panel, expected):
    game = make_game(assets, size=3)
    game.panel_manager.current_panel = panel

    game.on_exit_request()

    assert game.panel_manager.current_panel == expected


def test_on_exit_request_from_audio_settings_restores_snapshotted_volumes(assets):
    game = make_game(assets, size=3)
    game.panel_manager.current_panel = "audio_settings"
    game.audio._music, game.audio._sfx = 0.9, 0.9
    game.old_music_volume, game.old_sfx_volume = 0.2, 0.3

    game.on_exit_request()

    assert (game.audio._music, game.audio._sfx) == (0.2, 0.3)
    assert game.panel_manager.current_panel == "settings"


def test_on_exit_request_from_game_closes_info_panel_instead_of_saving(assets):
    game = make_game(assets, size=3)
    game.panel_manager.current_panel = "game"
    game.info_panel.is_active = True
    game.save_game = Spy()

    game.on_exit_request()

    assert len(game.info_panel.close.calls) == 1
    assert len(game.save_game.calls) == 0
    assert game.panel_manager.current_panel == "game"  # unchanged -- just closed the panel


def test_on_exit_request_from_game_saves_and_returns_to_menu(assets):
    game = make_game(assets, size=3)
    game.panel_manager.current_panel = "game"
    game.info_panel.is_active = False
    game.save_game = Spy()

    game.on_exit_request()

    assert len(game.save_game.calls) == 1
    assert game.panel_manager.current_panel == "menu"
