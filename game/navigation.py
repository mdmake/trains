from math import sin, cos, radians
from typing import Callable

import yaml

from game.exceptions import ConfigError
from game.mathfunction import sign
from game.trainsystem import TrainSystem


class NavigationSystem(TrainSystem):
    """
    Класс навигации выдает всем остальным подсистемам координаты и курс.
    Считывает настройки из конфига (`_load_config`)или словаря (`_unpack_config`)

    Класс получает на вход управление в виде вектора желаемого передвижения за этот такт (`v`, `alpha`) и
    выдает новое местоположение основываясь на наличии или отсутствии препятствий и
    ограничений на скорость и угловую скорость
    """

    def __init__(
            self, x: float | int, y: float | int, alpha: float | int, config: str | dict
    ):
        self.x = x
        self.y = y
        self.alpha = alpha

        self._new_v = 0.0  # управление по v
        self._new_alpha = 0.0  # управление по alpha

        self.method = None  # метод для обнаружения коллизий
        self.method_kwargs = None  # аргументы для этого метода

        if isinstance(config, dict):
            self._unpack_config(config)
        else:
            self._load_config(config)

        self.v_max = self.config["v_max"]
        self.max_angle_speed = self.config["max_angle_speed"]
        self.collision = False

    def _unpack_config(self, config: dict):
        """
        Чтение конфигурации из словаря. Все угловые величины должны быть в радианах!

        :param config: Словарь с конфигурацией.
        """
        self.config = config.copy()

        for item in ['max_angle_speed', "v_max"]:
            if item not in self.config:
                raise ConfigError(f"{item} not in config")

    def _load_config(self, filename: str):
        """
        Чтение конфигурации из файла. Все угловые величины должны быть в градусах!

        :param filename: Путь к файлу конфигурации
        :return:
        """
        self.config = {}
        with open(filename, "r") as f:
            data = yaml.safe_load(f)["train"]["tth"]

        for item in ['max_angle_speed', "v_max"]:
            if item not in self.config:
                raise ConfigError(f"{item} not in config")

        self.config["max_angle_speed"] = radians(data["max_angle_speed"])

    def set_measurement_method(self, method: Callable, **kwargs):
        """
        Ссылка на метод для поиска коллизий.

        :param method: Метод для измерения дальности;
        :param kwargs: Аргументы этого метода.
        """
        self.method = method
        self.method_kwargs = kwargs

    def step_restriction(self) -> tuple[float, float, float, bool]:
        """
        Проверка возможности перемещения на новою позицию
        """

        v = min(self._new_v, self.v_max)
        alpha = self.alpha + sign(self._new_alpha) * min(
            abs(self._new_alpha - self.alpha), self.max_angle_speed
        )

        x = self.x + v * cos(alpha)
        y = self.y + v * sin(alpha)

        result = self.method((self.x, self.y), (x, y), **self.method_kwargs)
        if result:
            x, y = result
            return x, y, alpha, True
        return x, y, alpha, False

    def receive(self, query: dict):
        self._new_alpha = query["alpha"]
        self._new_v = query["v"]

    def step(self):
        self.x, self.y, self.alpha, self.collision = self.step_restriction()
        self._new_v = 0.0
        self._new_alpha = 0.0

    def send(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "alpha": self.alpha,
            "collision": self.collision,
        }

    def update_navigation(self, x: float | int, y: float | int, alpha: float | int):
        pass
