from game.train import Train
from game.sightingsystem import Laser
from game.train import Train


# def testing_measurement_none(coord_begin, coord_end):
#     return None
#
#
# def testing_measurement_coord(coord_begin, coord_end):
#     return 45, 45


def test_create_object():
    train = Train(0.0, (0.0, 0.0))
    assert train is not None


def test_system_test():
    train = Train(0.0, (0.0, 0.0))
    assert True
