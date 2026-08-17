from types import SimpleNamespace

from gameplay.buildings.building import Building, Buildings
from gameplay.tile_selector import TileSelector
from gameplay.tilemap import Tilemap


def make_selector(assets, *, active=False):
    tilemap = Tilemap(size=3, max_size=7)
    mouse = SimpleNamespace(position=(-9999, -9999))
    buildings = Buildings(assets)
    selector = TileSelector(tilemap, mouse, buildings)
    selector.is_active = active
    return selector, tilemap, mouse, buildings


def test_get_hovered_tile_is_none_when_the_mouse_is_over_nothing(assets):
    selector, *_ = make_selector(assets)
    assert selector.get_hovered_tile() is None


def test_get_hovered_tile_finds_the_tile_under_the_mouse(assets):
    selector, tilemap, mouse, _ = make_selector(assets)
    target = tilemap[1][2]
    mouse.position = target.unselected_rect.center

    assert selector.get_hovered_tile() is target


def test_update_selection_marks_only_the_hovered_tile_selected(assets):
    selector, tilemap, mouse, _ = make_selector(assets, active=True)
    target = tilemap[0][1]
    mouse.position = target.unselected_rect.center

    selector.update_selection()

    assert target.selected is True
    assert target.rect == target.selected_rect
    others = [t for row in tilemap for t in row if t is not target]
    assert all(t.selected is False for t in others)
    assert all(t.rect == t.unselected_rect for t in others)


def test_update_selection_keeps_the_unselected_rect_when_the_selector_is_inactive(assets):
    selector, tilemap, mouse, _ = make_selector(assets, active=False)
    target = tilemap[0][0]
    mouse.position = target.unselected_rect.center

    selector.update_selection()

    # Hovered still, but selector itself is off -- rect must stay grounded,
    # not lift into the hover position (matches TileSelector.update_selection's
    # `tile.selected and self.is_active` guard).
    assert target.selected is True
    assert target.rect == target.unselected_rect


def test_get_selected_tile_returns_none_when_nothing_is_selected(assets):
    selector, *_ = make_selector(assets)
    assert selector.get_selected_tile() is None


def test_get_selected_building_returns_none_without_a_selected_tile(assets):
    selector, *_ = make_selector(assets)
    assert selector.get_selected_building() is None


def test_get_selected_building_matches_the_building_on_the_selected_tile(assets):
    selector, tilemap, mouse, buildings = make_selector(assets, active=True)
    tile = tilemap[1][1]
    building = Building(1, 0, tile)
    buildings.append(building)
    mouse.position = tile.unselected_rect.center

    selector.update_selection()

    assert selector.get_selected_building() is building


def test_get_selected_building_is_none_when_the_selected_tile_is_empty(assets):
    selector, tilemap, mouse, buildings = make_selector(assets, active=True)
    occupied_tile = tilemap[0][0]
    buildings.append(Building(1, 0, occupied_tile))
    empty_tile = tilemap[2][2]
    mouse.position = empty_tile.unselected_rect.center

    selector.update_selection()

    assert selector.get_selected_building() is None
