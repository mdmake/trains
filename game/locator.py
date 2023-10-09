from math import sin, cos
from collections import namedtuple
from typing import Any

LocatorQuery = namedtuple('LocatorQuery', ['position', 'point0', 'point1'])


class Locator:

    def __init__(self, range: float, blind_zone: float):
        # мертвая зона перед самом локатором -- зона где он ничего не видит
        self._blind_zone = blind_zone
        # максимальная дальность локатора
        self._range = range
        # последний запрос к локатору
        self._query = None
        # померянное расстояние до препятствия
        self._distance = None

    def make_query(self, x: float, y: float, alpha: float):
        """
        формируем запрос на измерение дальности, нам необходимо наше положение и угол от оси X
        """
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
        """
        внутренний метод, не использовать
        """
        self._distance = distance

    @property
    def measurement(self) -> dict[str, Any]:
        """
        Возвращает дальность до препятствия вместе с запросом по которому
        получена эта дальность
        """
        return {
            "query": self._query,
            "distance": self._distance}

    def range(self) -> float:
        # возвращает максимальную дальность локатора
        return self._range

    @property
    def blind_zone(self) -> float:
        """
        Возвращает размер мертвой зоны
        """

        return self._blind_zone

    @property
    def query(self) -> namedtuple:
        """
        Возвращает последний запрос
        """
        return self._query
