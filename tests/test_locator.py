from math import radians

from game.sightingsystem import Locator

EPS = 1e-6

full_config = {
    "min_range": 5,
    "max_range": 40,
    "max_angle_speed": radians(2),
    "cone_opening_angle": radians(120),
    "zero": radians(0),
    "place": [5, 15],
    "ray_count": 11,
    "ray_step": 6,
}


def measurement_method_no_collision(coord0, coord1, *args, **kwargs):
    return None


def measurement_method_collision(coord0, coord1, *args, **kwargs):
    x0, y0 = coord0
    x1, y1 = coord1

    x_col = (x1 - x0) * 0.8
    y_col = (y1 - y0) * 0.8

    return x_col, y_col


def test_create_locator_1():
    locator = Locator("test", "configs/locator_test.yaml")
    assert locator


def test_create_locator_2():
    locator = Locator("test", full_config)
    assert locator


def test_locator_step():
    laser = Locator("test", full_config)
    laser.set_measurement_method(measurement_method_no_collision)
    laser.update_navigation(0, 0, 0)
    laser.receive({})
    laser.step()
    ans = laser.send()
    assert ans == {}
