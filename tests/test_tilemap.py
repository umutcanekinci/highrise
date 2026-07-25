from gameplay.tilemap import Tilemap


def test_creates_a_size_by_size_grid_with_1_indexed_coordinates(assets):
    tm = Tilemap(size=3, max_size=7)

    assert tm.row_count == 3
    assert tm.column_count == 3
    assert len(tm) == 3
    assert all(len(row) == 3 for row in tm)
    assert tm[0][0].row_number == 1
    assert tm[0][0].column_number == 1
    assert tm[2][2].row_number == 3
    assert tm[2][2].column_number == 3


def test_expand_grows_by_one_in_each_dimension(assets):
    tm = Tilemap(size=3, max_size=7)
    tm.expand()
    assert (tm.row_count, tm.column_count) == (4, 4)
    assert len(tm) == 4 and len(tm[0]) == 4


def test_expand_is_a_no_op_once_max_size_reached(assets):
    tm = Tilemap(size=7, max_size=7)
    assert tm.is_max_size()

    tm.expand()

    assert (tm.row_count, tm.column_count) == (7, 7)


def test_is_max_size_true_if_either_dimension_hits_the_cap(assets):
    tm = Tilemap(size=5, max_size=7)
    tm.row_count = 7  # simulate an asymmetric grid
    assert tm.is_max_size()


def test_expand_cost_scales_with_current_row_count(assets):
    tm = Tilemap(size=3, max_size=7)
    assert tm.get_expand_cost() == (3 + 1) * 100

    tm.expand()
    assert tm.get_expand_cost() == (4 + 1) * 100


def test_expand_rows_only_grows_rows(assets):
    tm = Tilemap(size=3, max_size=7)
    tm.expand_rows()
    assert (tm.row_count, tm.column_count) == (4, 3)


def test_expand_rows_stops_at_max_row_count(assets):
    tm = Tilemap(size=3, max_size=7)
    tm.max_row_count = 3  # already at its own cap, independent of column cap
    tm.expand_rows()
    assert tm.row_count == 3


def test_expand_columns_only_grows_columns(assets):
    tm = Tilemap(size=3, max_size=7)
    tm.expand_columns()
    assert (tm.row_count, tm.column_count) == (3, 4)


def test_no_tile_selected_on_a_fresh_tilemap(assets):
    tm = Tilemap(size=3, max_size=7)
    assert tm.is_there_selected_tile() is False


def test_is_there_selected_tile_detects_any_selected_tile(assets):
    tm = Tilemap(size=2, max_size=7)
    tm[1][0].selected = True
    assert tm.is_there_selected_tile() is True
