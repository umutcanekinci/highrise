"""GamePersistenceMixin -- FakeGame subclasses the mixin directly (same
approach as test_game_events.py) against a real pygamine.Database pointed at
pytest's tmp_path, so save/load round-trips exercise real SQL rather than a
mocked connection. add_building() (defined on Game itself, not this mixin)
is stubbed to build a real Building against the real Tilemap load_game_data()
constructs, close enough to the real thing for persistence-level assertions."""

from types import SimpleNamespace

import pytest

from app.game_persistence import GamePersistenceMixin
from gameplay.buildings.building import Building, Buildings
from pygamine import Database


class FakeAudio:
    def __init__(self, music=0.5, sfx=0.5):
        self._music = music
        self._sfx = sfx

    def music_volume(self) -> float:
        return self._music

    def sfx_volume(self) -> float:
        return self._sfx

    def set_music_volume(self, value) -> None:
        self._music = value

    def set_sfx_volume(self, value) -> None:
        self._sfx = value


class FakeGame(GamePersistenceMixin):
    def __init__(self, tmp_path, assets, *, starting_money=500,
                 default_music=0.5, default_sfx=0.5, max_size=7):
        self.database = Database("test_persistence", directory=str(tmp_path))
        self.starting_money = starting_money
        self.default_music_volume = default_music
        self.default_sfx_volume = default_sfx
        self.max_size = max_size
        self.player = SimpleNamespace(money=0)
        self.audio = FakeAudio(default_music, default_sfx)
        self.tilemap = None
        self.tile_selector = SimpleNamespace(tilemap=None)
        self.buildings = Buildings(assets)
        self.calls: list = []

    def add_building(self, level, row, column) -> None:
        self.calls.append(("add_building", level, row, column))
        tile = self.tilemap[row - 1][column - 1]
        self.buildings.append(Building(level, self.buildings.age_number, tile))


def insert_building_row(game, level, row, column):
    game.database.execute_safely(
        "INSERT INTO buildings(level, row, column) VALUES (?, ?, ?)",
        params=(level, row, column),
    )


# ── init / seed ──────────────────────────────────────────────────────────────

def test_init_database_creates_empty_tables(tmp_path, assets):
    game = FakeGame(tmp_path, assets)

    game.init_database()

    assert game.database.execute_safely("SELECT * FROM game", True) == []
    assert game.database.execute_safely("SELECT * FROM buildings", True) == []


def test_get_game_data_seeds_a_default_row_on_first_call(tmp_path, assets):
    game = FakeGame(tmp_path, assets, starting_money=777)
    game.init_database()

    data = game.get_game_data()

    assert data == [(0, 2, 777, game.default_music_volume, game.default_sfx_volume)]


def test_get_game_data_returns_the_existing_row_on_later_calls(tmp_path, assets):
    game = FakeGame(tmp_path, assets)
    game.init_database()
    first = game.get_game_data()

    second = game.get_game_data()

    assert second == first


# ── load_data (top-level orchestrator) ──────────────────────────────────────

def test_load_data_bootstraps_a_brand_new_database_end_to_end(tmp_path, assets):
    game = FakeGame(tmp_path, assets, starting_money=250)

    game.load_data()

    assert game.player.money == 250
    assert game.tilemap is not None
    assert (game.tilemap.row_count, game.tilemap.column_count) == (2, 2)
    assert game.buildings == []


def test_load_data_restores_a_previously_saved_game(tmp_path, assets):
    seed = FakeGame(tmp_path, assets, starting_money=250)
    seed.load_data()
    seed.player.money = 999
    seed.buildings.age_number = 2
    seed.buildings.append(Building(3, 2, seed.tilemap[0][0]))
    seed.save_game()

    game = FakeGame(tmp_path, assets, starting_money=250)
    game.load_data()

    assert game.player.money == 999
    assert game.buildings.age_number == 2
    assert len(game.buildings) == 1
    assert game.buildings[0].level == 3


# ── load_game_data ───────────────────────────────────────────────────────────

def test_load_game_data_applies_saved_values(tmp_path, assets):
    game = FakeGame(tmp_path, assets, max_size=7)

    game.load_game_data([(3, 4, 250, 0.6, 0.2)])

    assert game.player.money == 250
    assert game.audio.music_volume() == 0.6
    assert game.audio.sfx_volume() == 0.2
    assert game.tilemap is not None
    assert (game.tilemap.row_count, game.tilemap.column_count) == (4, 4)
    assert game.tile_selector.tilemap is game.tilemap
    assert game.buildings.age_number == 3


def test_load_game_data_is_a_no_op_with_no_rows(tmp_path, assets):
    game = FakeGame(tmp_path, assets)

    game.load_game_data(None)
    game.load_game_data([])

    assert game.tilemap is None
    assert game.player.money == 0


# ── load_buildings ───────────────────────────────────────────────────────────

def test_load_buildings_restores_valid_rows_within_the_grid(tmp_path, assets):
    game = FakeGame(tmp_path, assets)
    game.init_database()
    game.load_game_data([(0, 3, 0, 0.5, 0.5)])  # 3x3 grid
    insert_building_row(game, 2, 1, 1)
    insert_building_row(game, 1, 3, 3)

    game.load_buildings()

    assert len(game.buildings) == 2
    assert ("add_building", 2, 1, 1) in game.calls
    assert ("add_building", 1, 3, 3) in game.calls


def test_load_buildings_deletes_out_of_bounds_rows_instead_of_restoring_them(tmp_path, assets):
    game = FakeGame(tmp_path, assets)
    game.init_database()
    game.load_game_data([(0, 3, 0, 0.5, 0.5)])  # 3x3 grid -- row/col must be 1..3
    insert_building_row(game, 1, 99, 99)  # out of bounds

    game.load_buildings()

    assert game.buildings == []
    assert game.calls == []
    remaining = game.database.execute_safely("SELECT * FROM buildings", True)
    assert remaining == []  # the bad row was deleted, not silently kept


def test_load_buildings_clears_any_existing_in_memory_buildings_first(tmp_path, assets):
    game = FakeGame(tmp_path, assets)
    game.init_database()
    game.load_game_data([(0, 3, 0, 0.5, 0.5)])
    game.buildings.append(Building(1, 0, game.tilemap[0][0]))  # stale in-memory state

    game.load_buildings()

    assert game.buildings == []  # no rows in the db -> cleared, not left stale


# ── save / delete ────────────────────────────────────────────────────────────

def test_save_audio_settings_persists_current_volumes(tmp_path, assets):
    game = FakeGame(tmp_path, assets)
    game.init_database()
    game.get_game_data()
    game.audio.set_music_volume(0.42)
    game.audio.set_sfx_volume(0.13)

    game.save_audio_settings()

    row = game.database.execute_safely("SELECT music_volume, sfx_volume FROM game", True)
    assert row == [(0.42, 0.13)]


def test_save_game_persists_state_and_buildings(tmp_path, assets):
    game = FakeGame(tmp_path, assets)
    game.init_database()
    game.get_game_data()  # seeds the row save_game()'s UPDATE needs to hit
    game.load_game_data([(0, 3, 0, 0.5, 0.5)])
    game.player.money = 900
    game.buildings.age_number = 2
    game.buildings.append(Building(3, 2, game.tilemap[1][1]))

    game.save_game()

    game_row = game.database.execute_safely("SELECT age_number, size, money FROM game", True)
    assert game_row == [(2, 3, 900)]
    building_rows = game.database.execute_safely("SELECT level, row, column FROM buildings", True)
    assert building_rows == [(3, 2, 2)]


def test_save_game_replaces_rather_than_accumulates_building_rows(tmp_path, assets):
    game = FakeGame(tmp_path, assets)
    game.init_database()
    game.get_game_data()
    game.load_game_data([(0, 3, 0, 0.5, 0.5)])
    game.buildings.append(Building(1, 0, game.tilemap[0][0]))
    game.save_game()

    game.buildings.clear()
    game.buildings.append(Building(2, 0, game.tilemap[2][2]))
    game.save_game()

    building_rows = game.database.execute_safely("SELECT level, row, column FROM buildings", True)
    assert building_rows == [(2, 3, 3)]


def test_delete_data_resets_the_game_row_and_clears_buildings(tmp_path, assets):
    game = FakeGame(tmp_path, assets, starting_money=500)
    game.init_database()
    game.get_game_data()
    game.load_game_data([(0, 3, 0, 0.5, 0.5)])
    game.buildings.append(Building(1, 0, game.tilemap[0][0]))
    game.save_game()

    game.delete_data()

    game_row = game.database.execute_safely("SELECT age_number, size, money FROM game", True)
    assert game_row == [(0, 2, 500)]
    building_rows = game.database.execute_safely("SELECT * FROM buildings", True)
    assert building_rows == []
