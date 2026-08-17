from gameplay.buildings.building import Building
from gameplay.tiles.tile import Tile
from ui.info_panel import InfoPanel


class FakeText:
    def __init__(self):
        self.text = None
        self.state = None

    def set_text(self, text, state=None) -> None:
        self.text = text
        self.state = state


class FakeImage:
    def __init__(self):
        self.surfaces = {}
        self.state = None

    def add_surface(self, name, surface) -> None:
        self.surfaces[name] = surface

    def set_state(self, state) -> None:
        self.state = state


class FakePanelManager(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_panel = "game"


def make_panel_manager():
    panel = {
        "level_text": FakeText(),
        "speed_text": FakeText(),
        "cooldown_text": FakeText(),
        "sell_price_text": FakeText(),
        "sell_button_text": FakeText(),
        "info_panel_building_image": FakeImage(),
    }
    return FakePanelManager({"game": panel}), panel


def test_new_info_panel_starts_active_with_no_building(assets):
    # GameObject defaults to active=True -- Game.run() explicitly calls
    # info_panel.close() right after construction to actually hide it.
    manager, _ = make_panel_manager()
    info_panel = InfoPanel(manager)

    assert info_panel.is_active is True
    assert info_panel.building is None


def test_open_and_close_toggle_is_active(assets):
    manager, _ = make_panel_manager()
    info_panel = InfoPanel(manager)

    info_panel.open()
    assert info_panel.is_active is True

    info_panel.close()
    assert info_panel.is_active is False


def test_refresh_writes_every_field_from_the_building(assets):
    manager, panel = make_panel_manager()
    info_panel = InfoPanel(manager)
    building = Building(level=2, age_number=1, tile=Tile(1, 1))

    info_panel.refresh(building)

    assert info_panel.building is building
    assert panel["level_text"].text == f"Level: {building.level}"
    assert panel["speed_text"].text == f"Speed: {building.speed} $/sec"
    assert panel["cooldown_text"].text == f"Cooldown: {building.cooldown} sec"
    assert panel["sell_price_text"].text == f"Sell Price: {building.sell_price}"
    assert panel["sell_button_text"].text == f"{building.sell_price}$"
    assert panel["sell_button_text"].state == "hover"
    assert panel["info_panel_building_image"].state == "default"
    assert "default" in panel["info_panel_building_image"].surfaces


def test_refresh_reads_from_whichever_panel_is_currently_open(assets):
    manager, panel = make_panel_manager()
    other_panel = {k: type(v)() for k, v in panel.items()}
    manager["other"] = other_panel
    manager.current_panel = "other"
    info_panel = InfoPanel(manager)
    building = Building(level=1, age_number=0, tile=Tile(1, 1))

    info_panel.refresh(building)

    assert other_panel["level_text"].text == f"Level: {building.level}"
    assert panel["level_text"].text is None  # untouched
