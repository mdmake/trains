from math import sin, cos, radians, remainder, tau, sqrt
from typing import Callable

import yaml

from game.exceptions import ConfigError
from game.mathfunction import sign, clamp
from game.trainsystem import TrainSystem

EPS = 1e-5


class NavigationSystem(TrainSystem):
    """
    Класс навигации выдает всем остальным подсистемам координаты и курс.
    Считывает настройки из конфига (`_load_config`)или словаря (`_unpack_config`)

    Класс получает на вход управление в виде вектора желаемого передвижения за этот такт (`v`, `alpha`) и
    выдает новое местоположение основываясь на наличии или отсутствии препятствий и
    ограничений на скорость и угловую скорость

    Скорость приводится к диапазону [0 .. max_v]
    Углы приводятся к диапазону [-pi .. pi]
    """

    def __init__(
        self, x: float | int, y: float | int, alpha: float | int, config: str | dict
    ):
        self.v = 0
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

        for item in ["max_angle_speed", "v_max"]:
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

        for item in ["max_angle_speed", "v_max"]:
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

    def step_restriction(self) -> tuple[float, float, float, float, bool]:
        """
        Проверка возможности перемещения на новою позицию
        """

        # ограничиваем v диапазоном [0, .. self.v_max]
        v = clamp(0.0, self._new_v, self.v_max)
        # ограничиваем alpha диапазоном [-pi, .. pi]
        new_alpha = remainder(self._new_alpha, tau)

        if new_alpha * self.alpha > 0:
            alpha = self.alpha + sign(new_alpha - self.alpha) * min(
                abs(new_alpha - self.alpha), self.max_angle_speed
            )
        else:
            delta = min(
                abs(new_alpha) + abs(self.alpha),
                tau - abs(new_alpha) - abs(self.alpha),
                self.max_angle_speed,
            )

            # выбираем направление кратчайшего доворота:
            if abs(new_alpha) + abs(self.alpha) < tau - abs(new_alpha) - abs(
                self.alpha
            ):
                signum = sign(self.alpha) if self.alpha != 0 else sign(-new_alpha)
                alpha = self.alpha - signum * delta
            else:
                alpha = self.alpha + sign(self.alpha) * delta

        alpha = remainder(alpha, tau)

        x0 = self.x + 0.02 * cos(alpha)
        y0 = self.y + 0.02 * sin(alpha)

        x1 = self.x + v * cos(alpha)
        y1 = self.y + v * sin(alpha)

        result = self.method((x0, y0), (x1, y1), **self.method_kwargs)
        if v > EPS and result:
            x, y = result.point

            # идея - если мы сталкиваемся с чем-то
            # сделав шаг - то мы не делаем этот шаг
            x = self.x
            y = self.y

            return x, y, alpha, v, True
        return x1, y1, alpha, v, False

    def receive(self, query: dict):
        """
        Получение данных.
        Получаем управляющие сигналы - скорость и угол.
        """
        self._new_alpha = query.get("alpha", self.alpha)
        self._new_v = query.get("v", self.v)

    def step(self):
        """
        Каждый шаг ограничиваем скорость и угол диапазоном и проверяем,
        можем ли мы шагнуть в этом направлении
        :return:
        """
        self.x, self.y, self.alpha, self.v, self.collision = self.step_restriction()
        self._new_v = 0.0
        self._new_alpha = 0.0

    def send(self) -> dict:
        """
        Посылка данных:

        x, y - собственные координаты в глобальной системе координат
        alpha - угол поворота в диапазоне [-pi .. pi]
        collision - произошло ли столкновение с препятствием на этом шаге
        """
        return {
            "x": self.x,
            "y": self.y,
            "alpha": self.alpha,
            "collision": self.collision,
        }

    def update_navigation(self, x: float | int, y: float | int, alpha: float | int):
        pass
