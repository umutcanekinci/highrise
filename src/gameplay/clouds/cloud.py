import random

from pygamine.image import load_image
from pygamine.asset_path import ImagePath, AssetPath
from pygamine.ecs.game_object_list import GameObjectList
from pygamine.ecs.game_object import GameObject
from pygamine.ecs.components.rigidbody2d import Rigidbody2D
from pygamine.ecs.components.sprite_renderer2d import SpriteRenderer2D


class Cloud(GameObject):
    def __init__(self, image_path: AssetPath, surface_size: tuple, size=(100, 100)):
        super().__init__()

        x = random.randint(0, surface_size[0] - 101)
        y = random.randint(0, surface_size[1] - 101)
        self.rect.size = size
        self.rect.set_position((x, y))
        self.add_component(SpriteRenderer2D).set_image(load_image(image_path, size))
        self.add_component(Rigidbody2D).set_velocity((random.choice([1/6, 1/7, 1/8, 1/9, 1/10, 1/11, 1/12, -1/6, -1/7, -1/8, -1/9, -1/10, -1/11, -1/12]), 0))
