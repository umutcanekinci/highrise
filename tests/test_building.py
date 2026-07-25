from pygame import Vector2

from gameplay.buildings.building import Building, ages
from gameplay.tiles.tile import Tile
from pygame_core.asset_path import ImagePath


def make_building(level=1, age_number=0, row=1, col=1) -> Building:
    return Building(level, age_number, Tile(row, col))


def test_speed_scales_with_level_and_age(assets):
    # speed = (level * 2 * (age_number + 1)) - 1
    assert make_building(level=1, age_number=0).speed == 1
    assert make_building(level=2, age_number=0).speed == 3
    assert make_building(level=1, age_number=1).speed == 3
    assert make_building(level=3, age_number=2).speed == 17


def test_sell_price_scales_with_level_and_age(assets):
    # sell_price = level * (age_number + 1) * 70
    assert make_building(level=1, age_number=0).sell_price == 70
    assert make_building(level=2, age_number=0).sell_price == 140
    assert make_building(level=1, age_number=3).sell_price == 280


def test_age_name_comes_from_the_ages_list(assets):
    for age_number, name in enumerate(ages):
        assert make_building(age_number=age_number).age == name


def test_floor_count_and_size_grow_every_two_levels(assets):
    b1 = make_building(level=1)
    b2 = make_building(level=2)
    b3 = make_building(level=3)

    assert b1.floor_count == 1
    assert b2.floor_count == 1  # (2+1)//2 == 1
    assert b3.floor_count == 2  # (3+1)//2 == 2
    assert b1.size == (50, 75)
    assert b3.size == (50, 75 + 23)  # one extra floor's worth of height


def test_get_image_path_reflects_level_and_age(assets):
    # AssetPath doesn't define __eq__, so compare the resolved filesystem
    # path each produces rather than object identity.
    b = make_building(level=3, age_number=1)
    assert str(b.get_image_path()) == str(ImagePath("level3", "buildings/rock"))


def test_payout_calls_on_payout_with_cooldown_times_speed(assets):
    b = make_building(level=2, age_number=0)  # speed == 3
    payouts = []
    b.on_payout = payouts.append

    b._payout()

    assert payouts == [b.cooldown * b.speed]


def test_payout_is_a_no_op_without_a_listener(assets):
    b = make_building()
    b.on_payout = None
    b._payout()  # must not raise


def test_level_up_moves_the_sacrificial_building_and_marks_it_for_destruction(assets):
    survivor    = make_building(level=2, row=1, col=1)
    sacrificial = make_building(level=2, row=2, col=2)

    survivor.level_up(sacrificial)

    assert sacrificial.tile is survivor.tile
    assert sacrificial.should_destroy is True
    assert sacrificial.new_building is survivor
    assert sacrificial.rigidbody.velocity != Vector2(0, 0)
