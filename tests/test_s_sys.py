from game.sightingsystem import Locator, Laser
from math import radians

EPS = 1e-6


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
    config = {
        "min_range": 5,
        "max_range": 40,
        "max_angle_speed": radians(2),
        "cone_opening_angle": radians(120),
        "zero": radians(0),
        "ray_count": 11,
        "ray_step": 6,
    }
    locator = Locator("test", config)
    assert locator


def test_locator_1():
    pass


# def test_create_locator_3_failed():
#     config = {
#     }
#
#     locator = Locator("test", config)
#     assert locator


def test_create_laser_1():
    laser = Laser("test", "configs/laser_test.yaml")
    assert laser


def test_create_laser_2():
    config = {
        "min_range": 5,
        "max_range": 80,
        "max_angle_speed": 5,  # deg/turn
        "cone_opening_angle": 120,  # deg
        "zero": 0,
        "fire_power": 100,
        "fire_time_limit": 5,  # turns
        "max_angle_speed_tracking": 4,
    }

    laser = Laser("test", config)
    assert laser


# def test_create_laser_3_failed():
#     config = {
#     }
#
#     laser = Laser("test", config)
#     assert laser


def test_laser_1():
    config = {
        "min_range": 5,
        "max_range": 100,
        "max_angle_speed": radians(5),  # deg/turn
        "cone_opening_angle": radians(120),  # deg
        "zero": radians(0),
        "fire_power": 100,
        "fire_time_limit": 5,  # turns
        "max_angle_speed_tracking": 4,
    }

    laser = Laser("test", config)
    laser.set_measurement_method(measurement_method_no_collision)

    input_query = {"config": True}
    # TODO ???
    laser.processing_query(input_query)
    laser.update((1, 1), radians(0))
    query = laser.send_query()

    assert 'config' in query

    for key in config.keys():
        assert (query['config'][key] - config[key]) < EPS

    input_query = {"distance": True}
    laser.processing_query(input_query)
    query = laser.send_query()

    assert 'measurement' in query
    assert abs(query['measurement']['distance'] - config['max_range']) < EPS
    assert query['measurement']['obstacle'] is False




