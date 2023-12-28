from game.exceptions import ConfigError

from game.sightingsystem import Laser

from math import radians, degrees

EPS = 1e-6

full_config = {
    "min_range": 0,
    "max_range": 15,
    "max_angle_speed": radians(5),
    "cone_opening_angle": radians(145),
    "zero": radians(10),
    "place": [5, 15],
    "fire_power": 100,
    "fire_time_limit": 5,
    "max_angle_speed_tracking": radians(4),
}


def measurement_method_no_collision(coord0, coord1, *args, **kwargs):
    return None


def measurement_method_collision(coord0, coord1, *args, **kwargs):
    x0, y0 = coord0
    x1, y1 = coord1

    x_col = (x1 - x0) * 0.8
    y_col = (y1 - y0) * 0.8

    return x_col, y_col


def test_create_laser_1():
    laser = Laser("test", "configs/laser_test.yaml")
    assert laser


def test_create_laser_2():
    laser = Laser("test", full_config)
    assert laser


def test_create_laser_with_incomplete_config():
    config = {
        "min_range": 5,
        "max_range": 80,
        "max_angle_speed": 5,  # deg/turn
        "cone_opening_angle": 120,  # deg
        "fire_power": 100,
        "fire_time_limit": 5,  # turns
        "max_angle_speed_tracking": 4,
    }
    try:
        Laser("test", config)
    except ConfigError as e:
        message_set = set(str(e).strip().replace("'", " ").replace('"', " ").split())
        assert message_set & set(full_config.keys()) == {"place", "zero"}
        return
    assert False


def test_laser_step():
    laser = Laser("test", full_config)
    laser.update_navigation(0, 0, 0)
    laser.receive({})
    laser.step()
    ans = laser.send()
    assert ans == {}


def test_laser_step_math_test():
    config = {
        "min_range": 0,
        "max_range": 15,
        "max_angle_speed": radians(5),  # deg/turn
        "cone_opening_angle": radians(145),  # deg
        "zero": radians(10),
        "place": [5, 15],
        "fire_power": 100,
        "fire_time_limit": 5,  # turns
        "max_angle_speed_tracking": radians(4),
    }

    query = {"turn": radians(-90), "distance": True}

    laser = Laser("test", config)
    laser.set_measurement_method(measurement_method_no_collision)

    laser.update_navigation(0, 0, 0)
    laser.receive(query)
    laser.step()
    ans = laser.send()

    alpha = degrees(ans["alpha"]["value"])

    assert abs(ans["alpha"]["value"] - query["turn"]) < EPS
    assert abs(ans["distance"][0]["x"] - 5.0) < EPS
    assert abs(ans["distance"][0]["y"] - 0.0) < EPS
