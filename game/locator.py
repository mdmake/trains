from math import sin, cos
from collections import namedtuple
from typing import Any

LocatorQuery = namedtuple('LocatorQuery', ['position', 'point0', 'point1'])


class Locator:
    def __init__(self, range: float, blind_zone: float):
        self._blind_zone = blind_zone
        self._range = range
        self._query = None
        self._distance = None

    def make_query(self, x: float, y: float, alpha: float):
        end_point = (
            x + self._range * cos(alpha),
            y + self._range * sin(alpha)
        )
        begin_point = (
            x + self._blind_zone * cos(alpha),
            y + self._blind_zone * sin(alpha)
        )
        self._query = LocatorQuery((x, y, alpha), begin_point, end_point)

    def _set_distance(self, distance):
        self._distance = distance

    @property
    def measurement(self) -> dict[str, Any]:
        return {
            "query": self._query,
            "distance": self._distance}

    def range(self) -> float:
        return self._range

    @property
    def blind_zone(self) -> float:
        return self._blind_zone

    @property
    def query(self) -> namedtuple:
        return self._query
