from geometry.geometry import Point


def test_point_1():
    assert (Point(1, 1) in [Point(1, 2), Point(1, 4), Point(1, 5)]) is False
    assert (Point(1, 1) in [Point(1, 1), Point(1, 4), Point(1, 5)]) is True
