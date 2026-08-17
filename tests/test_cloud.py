from pygamine import ImagePath, Rigidbody2D

from gameplay.clouds.cloud import Cloud
from gameplay.clouds.cloud_container import CloudContainer, LoopingCloudAnimation, OneShotCloudAnimation

SURFACE_SIZE = (800, 600)


def test_cloud_spawns_within_bounds_and_gets_a_horizontal_only_velocity():
    cloud = Cloud(ImagePath("cloud"), SURFACE_SIZE)

    assert 0 <= cloud.rect.x <= SURFACE_SIZE[0] - 101
    assert 0 <= cloud.rect.y <= SURFACE_SIZE[1] - 101
    rb = cloud.get_component(Rigidbody2D)
    assert rb.velocity.y == 0
    assert abs(rb.velocity.x) in (1/6, 1/7, 1/8, 1/9, 1/10, 1/11, 1/12)


def test_cloud_uses_the_requested_size():
    cloud = Cloud(ImagePath("cloud"), SURFACE_SIZE, size=(40, 40))
    assert cloud.rect.size == (40, 40)


# ── CloudContainer ───────────────────────────────────────────────────────────

def test_remove_offscreen_drops_clouds_past_either_edge():
    container = CloudContainer(SURFACE_SIZE)
    off_right = Cloud(ImagePath("cloud"), SURFACE_SIZE)
    off_right.rect.x = SURFACE_SIZE[0]
    off_left = Cloud(ImagePath("cloud"), SURFACE_SIZE)
    off_left.rect.x = -off_left.rect.width
    on_screen = Cloud(ImagePath("cloud"), SURFACE_SIZE)
    on_screen.rect.x = SURFACE_SIZE[0] // 2
    container.extend([off_right, off_left, on_screen])

    container._remove_offscreen()

    assert list(container) == [on_screen]


# ── LoopingCloudAnimation ────────────────────────────────────────────────────

def test_create_clouds_populates_the_requested_count():
    anim = LoopingCloudAnimation(5, SURFACE_SIZE)
    assert len(anim) == 5


def test_update_spawns_a_wrap_companion_once_a_cloud_crosses_the_right_edge():
    anim = LoopingCloudAnimation(0, SURFACE_SIZE)
    cloud = anim._new_cloud()
    cloud.rect.x = SURFACE_SIZE[0] - cloud.rect.width + 1  # already past the right edge
    cloud.get_component(Rigidbody2D).set_velocity((1, 0))  # moving right
    anim.append(cloud)

    anim.update()

    assert len(anim) == 2  # the original plus its wrap companion
    assert id(cloud) in anim._companions


def test_update_only_spawns_one_companion_per_crossing():
    anim = LoopingCloudAnimation(0, SURFACE_SIZE)
    cloud = anim._new_cloud()
    cloud.rect.x = SURFACE_SIZE[0] - cloud.rect.width + 1
    cloud.get_component(Rigidbody2D).set_velocity((1, 0))
    anim.append(cloud)

    anim.update()
    anim.update()

    assert len(anim) == 2  # not 3 -- already companioned, no duplicate spawn


def test_remove_offscreen_also_forgets_the_companion_flag():
    anim = LoopingCloudAnimation(0, SURFACE_SIZE)
    cloud = anim._new_cloud()
    cloud.rect.x = SURFACE_SIZE[0]  # already off the right edge
    anim._companions.add(id(cloud))
    anim.append(cloud)

    anim._remove_offscreen()

    assert list(anim) == []
    assert id(cloud) not in anim._companions


# ── OneShotCloudAnimation ────────────────────────────────────────────────────

def test_one_shot_creates_a_hundred_clouds_moving_away_from_center():
    # Unlike LoopingCloudAnimation, OneShotCloudAnimation.__init__ doesn't
    # call create_clouds() itself -- Game.open_panel() triggers it explicitly
    # on each panel transition.
    anim = OneShotCloudAnimation(SURFACE_SIZE)
    anim.create_clouds()

    assert len(anim) == 100
    for cloud in anim:
        rb = cloud.get_component(Rigidbody2D)
        if cloud.rect.x <= SURFACE_SIZE[0] / 2:
            assert rb.velocity.x == -10
        else:
            assert rb.velocity.x == 10


def test_one_shot_update_eventually_empties_as_clouds_leave_the_screen():
    anim = OneShotCloudAnimation(SURFACE_SIZE)
    anim.create_clouds()
    # Force every cloud far enough that even one big timestep clears the
    # screen -- update()'s own per-frame speed is realistically small, so
    # this pushes clouds out by hand rather than looping hundreds of frames.
    for cloud in anim:
        cloud.rect.x = SURFACE_SIZE[0] + 10 if cloud.rect.x > SURFACE_SIZE[0] / 2 else -cloud.rect.width - 10

    anim.update()

    assert len(anim) == 0
