from copy import deepcopy
from math import radians, cos, sin, sqrt, remainder, tau
from typing import Callable

import yaml

from game.exceptions import ConfigError
from game.trainsystem import TrainSystem


class SightingSystem(TrainSystem):
    """
    Базовый класс для всех визирных подcистем:
    Каждая подсистема должна:
     - получать информацию о местоположении и ориентации борта (`update_navigation`),
     - получать данные (`receive`),
     - производить обработку данных на текущем такте (`step`),
     - посылать данные (`send`).
     - загружать свою конфигурацию из словаря (`_unpack_config`) или файла (`_load_config`)
    """

    def __init__(self, name: str, config: str | dict):
        self.name = name

        self.method_kwargs = None
        self.method = None

        # координаты борта
        self.ship_x = None
        self.ship_y = None
        self.ship_alpha = None

        # координаты подсистемы в абсолютной системе координат
        self.alpha = None
        self.x = None
        self.y = None

        # координаты подсистемы в связанной с бортом системе координат
        self.ssk_x = None
        self.ssk_y = None
        self.ssk_alpha = None

        # сдвиг точки посадки относительно центра масс
        self.shift_x, self.shift_y = None, None
        self.shift_alpha = None

        self.query_data = {}
        self.query = {}

        if isinstance(config, dict):
            self._unpack_config(config)
        else:
            self._load_config(config)

    def _unpack_config(self, data: dict):
        raise NotImplementedError

    def _load_config(self, data: str):
        raise NotImplementedError

    def set_measurement_method(self, method: Callable, **kwargs):
        self.method = method
        self.method_kwargs = kwargs

    def update_navigation(self, x: float | int, y: float | int, alpha: float | int):
        """
        Обновление навигационной информации

        :param x: координата x борта в абсолютной СК
        :param y: координата y борта в абсолютной СК
        :param alpha: угол поворота в абсолютной СК от оси х, против часовой стрелки
        """
        self.ship_x = x
        self.ship_y = y
        self.ship_alpha = alpha

    def send(self):
        return self.query_data

    def receive(self, query: dict):
        self.query = deepcopy(query)


class Laser(SightingSystem):
    """
    Подсистема 'Лазер'

    Умеет мерить дальность в заданно направлении, брать точку в захват и сопровождать ее.
    """

    def __init__(self, name: str, config: str | dict):
        self.required_fields = {
            "min_range",
            "max_range",
            "max_angle_speed",
            "zero",
            "place",
            "fire_power",
            "cone_opening_angle",
            "fire_time_limit",
            "max_angle_speed_tracking",
        }

        super().__init__(name, config)

        self.min_range = self.config["min_range"]
        self.max_range = self.config["max_range"]
        self.shift_x, self.shift_y = self.config["place"]
        self.fire_time_limit = self.config["fire_time_limit"]

        self.ssk_alpha = 0.0

        # точка замера лазером в нск
        self.point_x = None
        self.point_y = None

        # точка замера лазером в сск
        self.point_x_ssk = None
        self.point_y_ssk = None

        # есть точка или нет
        self.measurement = False

    def _unpack_config(self, data: dict):
        self.config = data.copy()

        if self.required_fields - self.config.keys():
            raise ConfigError(
                f"Incomplete config, {self.required_fields - self.config.keys()} not in config"
            )

        self.max_angle_speed = self.config["max_angle_speed"]
        self.max_angle_speed_tracking = self.config["max_angle_speed_tracking"]
        self.shift_alpha = self.config["zero"]
        self.cone_opening_angle_left = self.config["cone_opening_angle"]
        self.cone_opening_angle_right = -self.config["cone_opening_angle"]

    def _load_config(self, filename):
        with open(filename, "r") as f:
            self.config = yaml.safe_load(f)["laser"]

        if self.required_fields - self.config.keys():
            raise KeyError(
                f"incomplete config, {self.required_fields - self.config.keys()} not in config"
            )

        self.max_angle_speed = radians(self.config["max_angle_speed"])
        self.max_angle_speed_tracking = radians(self.config["max_angle_speed_tracking"])
        self.cone_opening_angle_left = radians(self.config["cone_opening_angle"])
        self.cone_opening_angle_right = -radians(self.config["cone_opening_angle"])
        self.shift_alpha = radians(self.config["zero"])

    def step(self):
        # обновляем собственные координаты в нск
        self.x = (
            self.ship_x
            + self.shift_x * cos(self.ship_alpha)
            - self.shift_y * sin(self.ship_alpha)
        )
        self.y = (
            self.ship_y
            + self.shift_x * sin(self.ship_alpha)
            + self.shift_y * cos(self.ship_alpha)
        )

        # обновляем собственный угол в нск:
        # угол поврота борта + установочный угол + угол поворота относительно собственной оси
        self.alpha = self.ssk_alpha + self.shift_alpha + self.ship_alpha

        # команда не поворот лазера относительно строительной оси - приходит угол в абсолютной системе координат
        # нам дали команду поменять курс на новый, угол курса - self.query['turn]:
        if "turn" in self.query:
            restriction = None

            self.ssk_alpha = remainder(
                self.query["turn"] - self.shift_alpha - self.ship_alpha, tau
            )

            if self.ssk_alpha > self.cone_opening_angle_left:
                self.ssk_alpha = self.cone_opening_angle_left
                restriction = 1
            elif self.ssk_alpha < self.cone_opening_angle_right:
                self.ssk_alpha = self.cone_opening_angle_right
                restriction = -1

            self.alpha = remainder(
                self.ship_alpha + self.shift_alpha + self.ssk_alpha, tau
            )

            self.query_data["alpha"] = {}
            self.query_data["alpha"]["value"] = self.alpha
            self.query_data["alpha"]["restriction"] = restriction

        if self.query.get("distance", False):
            self.point_x = self.x + self.max_range * cos(self.alpha)
            self.point_y = self.y + self.max_range * sin(self.alpha)

            result = self.method(
                (self.x, self.y), (self.point_x, self.point_y), **self.method_kwargs
            )

            if result:
                self.point_x, self.point_y = result.point
                distance = sqrt(
                    (self.x - self.point_x) ** 2 + (self.y - self.point_y) ** 2
                )
                self.measurement = True
            else:
                distance = self.max_range
                self.measurement = False

            self.point_x_ssk = distance * cos(self.ssk_alpha)
            self.point_y_ssk = distance * sin(self.ssk_alpha)

            query_data = {
                "x": self.point_x,
                "y": self.point_y,
                "measurement": self.measurement,
                "ssk_x": self.point_x_ssk,
                "ssk_y": self.point_y_ssk,
                "value": distance,
            }

            self.query_data["distance"] = [
                query_data,
            ]


class Locator(SightingSystem):
    def __init__(self, name: str, config: str | dict):
        self.required_fields = {
            "min_range",
            "max_range",
            "max_angle_speed",
            "zero",
            "place",
            "cone_opening_angle",
            "ray_count",
            "ray_step",
        }
        self.query = None

        super().__init__(name, config)

        self.min_range = self.config["min_range"]
        self.max_range = self.config["max_range"]
        self.shift_x, self.shift_y = self.config["place"]
        self.ray_count = self.config["ray_count"]

        self.ssk_alpha = 0.0

        # точка замера лазером в нск
        self.point_x = [None] * self.ray_count
        self.point_y = [None] * self.ray_count

        # точка замера лазером в сск
        self.point_x_ssk = [None] * self.ray_count
        self.point_y_ssk = [None] * self.ray_count

        # есть точка или нет
        self.measurement = [False] * self.ray_count

    def _unpack_config(self, data: dict):
        self.config = data.copy()

        if self.required_fields - self.config.keys():
            raise ConfigError(
                f"Incomplete config, {self.required_fields - self.config.keys()} not in config"
            )

        self.max_angle_speed = self.config["max_angle_speed"]
        self.shift_alpha = self.config["zero"]
        self.cone_opening_angle_left = self.config["cone_opening_angle"]
        self.cone_opening_angle_right = -self.config["cone_opening_angle"]
        self.ray_step = self.config["ray_step"]

    def _load_config(self, filename):
        with open(filename, "r") as f:
            self.config = yaml.safe_load(f)["locator"]

        if self.required_fields - self.config.keys():
            raise KeyError(
                f"incomplete config, {self.required_fields - self.config.keys()} not in config"
            )

        self.max_angle_speed = radians(self.config["max_angle_speed"])
        self.cone_opening_angle_left = radians(self.config["cone_opening_angle"])
        self.cone_opening_angle_right = -radians(self.config["cone_opening_angle"])
        self.shift_alpha = radians(self.config["zero"])
        self.ray_step = radians(self.config["ray_step"])

    def step(self):
        # обновляем собственные координаты в нск
        self.x = (
            self.ship_x
            + self.shift_x * cos(self.ship_alpha)
            - self.shift_y * sin(self.ship_alpha)
        )
        self.y = (
            self.ship_y
            + self.shift_x * sin(self.ship_alpha)
            + self.shift_y * cos(self.ship_alpha)
        )

        # обновляем собственный угол в нск:
        # угол поврота борта + установочный угол + угол поворота относительно собственной оси
        self.alpha = self.ssk_alpha + self.shift_alpha + self.ship_alpha

        # команда не поворот лазера относительно строительной оси - приходит угол в абсолютной системе координат
        # нам дали команду поменять курс на новый, угол курса - self.query['turn]:
        if "turn" in self.query:
            restriction = None

            self.ssk_alpha = remainder(
                self.query["turn"] - self.shift_alpha - self.ship_alpha, tau
            )

            if self.ssk_alpha > self.cone_opening_angle_left:
                self.ssk_alpha = self.cone_opening_angle_left
                restriction = 1
            elif self.ssk_alpha < self.cone_opening_angle_right:
                self.ssk_alpha = self.cone_opening_angle_right
                restriction = -1

            self.alpha = remainder(
                self.ship_alpha + self.shift_alpha + self.ssk_alpha, tau
            )

            self.query_data["alpha"] = {}
            self.query_data["alpha"]["value"] = self.alpha
            self.query_data["alpha"]["restriction"] = restriction

        if self.query.get("distance", False):
            self.query_data["distance"] = []

            begin_angle = self.ssk_alpha - (self.ray_count - 1) * self.ray_step / 2

            for ray_num in range(self.ray_count):
                angle = (
                    self.ship_alpha
                    + self.shift_alpha
                    + begin_angle
                    + ray_num * self.ray_step
                )
                distance = self.max_range

                point_x = self.x + distance * cos(angle)
                point_y = self.y + distance * sin(angle)

                result = self.method(
                    (self.x, self.y), (point_x, point_y), **self.method_kwargs
                )

                if result:
                    point_x, point_y = result.point
                    distance = sqrt((self.x - point_x) ** 2 + (self.y - point_y) ** 2)
                    self.measurement[ray_num] = True
                else:
                    distance = self.max_range
                    self.measurement[ray_num] = False

                self.point_x_ssk[ray_num] = distance * cos(self.ssk_alpha)
                self.point_y_ssk[ray_num] = distance * sin(self.ssk_alpha)

                query_data = {
                    "x": point_x,
                    "y": point_y,
                    "measurement": self.measurement[ray_num],
                    "ssk_x": self.point_x_ssk[ray_num],
                    "ssk_y": self.point_y_ssk[ray_num],
                    "value": distance,
                }

                self.query_data["distance"].append(query_data)
