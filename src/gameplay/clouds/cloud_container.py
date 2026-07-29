from gameplay.clouds.cloud import Cloud
from pygamine import ImagePath
from pygamine import Rigidbody2D
from pygamine import GameObjectList


class CloudContainer(GameObjectList):
    def __init__(self, surface_size: tuple) -> None:
        super().__init__()
        self.surface_size = surface_size

    def _remove_offscreen(self) -> None:
        W = self.surface_size[0]
        for cloud in [c for c in self if c.rect.x >= W or c.rect.x + c.rect.width <= 0]:
            self.remove(cloud)


class LoopingCloudAnimation(CloudContainer):
    _cloud_image = ImagePath("cloud")

    def __init__(self, count: int, surface_size: tuple) -> None:
        super().__init__(surface_size)
        self._cloud_count = count
        self._companions: set[int] = set()
        self.create_clouds()

    def create_clouds(self) -> None:
        for _ in range(self._cloud_count):
            self.append(self._new_cloud())

    def _new_cloud(self) -> Cloud:
        return Cloud(self._cloud_image, self.surface_size)

    def _remove_offscreen(self) -> None:
        W = self.surface_size[0]
        for cloud in [c for c in self if c.rect.x >= W or c.rect.x + c.rect.width <= 0]:
            self._companions.discard(id(cloud))
            self.remove(cloud)

    def update(self) -> None:
        to_add = []
        W = self.surface_size[0]

        for cloud in self:
            rb = cloud.get_component(Rigidbody2D)
            assert rb is not None
            velocity = rb.velocity
            xvel = velocity.x
            x = cloud.rect.x
            y = cloud.rect.y
            width = cloud.rect.width

            if id(cloud) not in self._companions:
                if xvel > 0 and x + width > W:
                    self._companions.add(id(cloud))
                    companion = self._new_cloud()
                    companion.rect.topleft = (x - W, y)
                    companion.get_component(Rigidbody2D).set_velocity(velocity)
                    to_add.append(companion)
                elif xvel < 0 and x < 0:
                    self._companions.add(id(cloud))
                    companion = self._new_cloud()
                    companion.rect.topleft = (x + W, y)
                    companion.get_component(Rigidbody2D).set_velocity(velocity)
                    to_add.append(companion)

            cloud.update()

        for cloud in to_add:
            self.append(cloud)

        self._remove_offscreen()


class OneShotCloudAnimation(CloudContainer):
    def __init__(self, surface_size: tuple) -> None:
        super().__init__(surface_size)

    def create_clouds(self) -> None:
        for _ in range(100):
            cloud = Cloud(ImagePath("cloud"), self.surface_size, (200, 200))
            xvel = -10 if cloud.rect.x <= self.surface_size[0] / 2 else 10
            cloud.get_component(Rigidbody2D).set_velocity((xvel, 0))
            self.append(cloud)

    def update(self) -> None:
        self._remove_offscreen()
        super().update()