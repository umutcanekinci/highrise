"""Buildings.move() is the core 2048-style slide/merge mechanic: buildings
in a row or column slide toward the moved-toward edge, and equal-level
adjacent buildings merge. move() resolves the grid assignment (.tile) and
merge intent (.should_destroy/.new_building) synchronously; only the visual
glide is animated frame-by-frame via control_moving(), which is tested
separately below without needing to simulate that animation."""

from pygame import Vector2

from gameplay.buildings.building import Building, Buildings
from gameplay.tilemap import Tilemap

MAX_LEVEL = 6


def make_grid(assets, size=3):
    return Buildings(assets), Tilemap(size=size, max_size=size)


def place(buildings: Buildings, tilemap: Tilemap, level: int, row: int, col: int) -> Building:
    b = Building(level, 0, tilemap[row - 1][col - 1])
    buildings.append(b)
    return b


def test_move_left_slides_a_lone_building_to_the_first_column(assets):
    buildings, tilemap = make_grid(assets)
    b = place(buildings, tilemap, level=1, row=1, col=3)

    buildings.move("left", tilemap, MAX_LEVEL)

    assert (b.tile.row_number, b.tile.column_number) == (1, 1)
    assert b.should_destroy is False


def test_move_right_slides_a_lone_building_to_the_last_column(assets):
    buildings, tilemap = make_grid(assets)
    b = place(buildings, tilemap, level=1, row=1, col=1)

    buildings.move("right", tilemap, MAX_LEVEL)

    assert (b.tile.row_number, b.tile.column_number) == (1, 3)


def test_move_up_slides_a_lone_building_to_the_first_row(assets):
    buildings, tilemap = make_grid(assets)
    b = place(buildings, tilemap, level=1, row=3, col=1)

    buildings.move("up", tilemap, MAX_LEVEL)

    assert (b.tile.row_number, b.tile.column_number) == (1, 1)


def test_move_down_slides_a_lone_building_to_the_last_row(assets):
    buildings, tilemap = make_grid(assets)
    b = place(buildings, tilemap, level=1, row=1, col=1)

    buildings.move("down", tilemap, MAX_LEVEL)

    assert (b.tile.row_number, b.tile.column_number) == (3, 1)


def test_equal_level_buildings_merge_on_collision(assets):
    buildings, tilemap = make_grid(assets)
    survivor    = place(buildings, tilemap, level=1, row=1, col=1)
    sacrificial = place(buildings, tilemap, level=1, row=1, col=2)

    buildings.move("left", tilemap, MAX_LEVEL)

    assert survivor.tile.column_number == 1
    assert survivor.should_destroy is False
    assert sacrificial.tile is survivor.tile  # slid onto the survivor's tile
    assert sacrificial.should_destroy is True
    assert sacrificial.new_building is survivor


def test_different_level_buildings_pack_adjacent_without_merging(assets):
    buildings, tilemap = make_grid(assets)
    low  = place(buildings, tilemap, level=1, row=1, col=1)
    high = place(buildings, tilemap, level=2, row=1, col=3)

    buildings.move("left", tilemap, MAX_LEVEL)

    assert low.tile.column_number == 1
    assert high.tile.column_number == 2  # packed next to `low`, not merged
    assert low.should_destroy is False
    assert high.should_destroy is False


def test_buildings_already_at_max_level_do_not_merge(assets):
    buildings, tilemap = make_grid(assets)
    a = place(buildings, tilemap, level=MAX_LEVEL, row=1, col=1)
    b = place(buildings, tilemap, level=MAX_LEVEL, row=1, col=3)

    buildings.move("left", tilemap, MAX_LEVEL)

    assert a.tile.column_number == 1
    assert b.tile.column_number == 2  # packed adjacent, not merged
    assert a.should_destroy is False
    assert b.should_destroy is False


def test_move_is_a_no_op_while_a_previous_move_is_still_animating(assets):
    buildings, tilemap = make_grid(assets)
    b = place(buildings, tilemap, level=1, row=1, col=3)

    buildings.move("left", tilemap, MAX_LEVEL)
    assert buildings.is_moving()  # velocity set by set_target_tile, not yet settled

    buildings.move("right", tilemap, MAX_LEVEL)  # should be ignored entirely

    assert (b.tile.row_number, b.tile.column_number) == (1, 1)


def test_control_moving_finalizes_a_settled_merge_into_a_leveled_up_building(assets):
    buildings, tilemap = make_grid(assets)
    tile = tilemap[0][0]
    survivor    = Building(2, 0, tile)
    sacrificial = Building(2, 0, tile)
    sacrificial.should_destroy = True
    sacrificial.new_building = survivor
    # Both still have their construction-time (0, 0) velocity -- simulates
    # the glide animation having already reached its target.
    buildings.extend([survivor, sacrificial])

    buildings.control_moving()

    assert survivor not in buildings
    assert sacrificial not in buildings
    assert len(buildings) == 1
    merged = buildings[0]
    assert merged.level == 3
    assert merged.tile is tile


def test_control_moving_settles_a_building_that_reached_its_target(assets):
    buildings, tilemap = make_grid(assets)
    b = place(buildings, tilemap, level=1, row=1, col=1)
    b.set_target_tile(tilemap[0][2])  # starts gliding toward column 3
    assert b.rigidbody.velocity != Vector2(0, 0)
    # Snap it to (just past) the target position, as if a frame's worth of
    # movement had already carried it there.
    b.rect.topleft = (int(b.target_position.x), int(b.target_position.y))

    buildings.control_moving()

    assert b.rigidbody.velocity == Vector2(0, 0)
    assert tuple(b.rect.topleft) == (int(b.target_position.x), int(b.target_position.y))
