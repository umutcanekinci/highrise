from pygamine.image import load_image
from pygamine.ecs.game_object import GameObject
from gameplay.buildings.building import Building


class InfoPanel:
    def __init__(self, panel_manager) -> None:
        self.panel_manager = panel_manager
        self.root = GameObject("info_panel")
        self.building: Building | None = None

    def refresh(self, building: Building) -> None:
        self.building = building
        panel = self.panel_manager[self.panel_manager.current_panel]
        panel["level_text"].set_text("Level: " + str(building.level))
        panel["speed_text"].set_text("Speed: " + str(building.speed) + " $/sec")
        panel["cooldown_text"].set_text("Cooldown: " + str(building.cooldown) + " sec")
        panel["sell_price_text"].set_text("Sell Price: " + str(building.sell_price))
        panel["sell_button_text"].set_text(str(building.sell_price) + "$", state="hover")
        panel["info_panel_building_image"].add_surface("default", load_image(building.get_image_path(), (65, 89)))
        panel["info_panel_building_image"].set_state("default")

    def open(self) -> None:
        self.root.active = True

    def close(self) -> None:
        self.root.active = False

    @property
    def is_active(self) -> bool:
        return self.root.active