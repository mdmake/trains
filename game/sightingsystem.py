from copy import deepcopy
from math import radians, cos, sin, sqrt
from typing import Callable

import yaml

from game.exceptions import ConfigError
from game.mathfunction import sign
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
        self.query = None

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

    def receive(self, query):
        self.query = deepcopy(query)

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

            delta = self.query["turn"] - self.alpha

            self.ssk_alpha = self.query["turn"] - self.shift_alpha

            if self.ssk_alpha > self.cone_opening_angle_left:
                self.ssk_alpha = self.cone_opening_angle_left
                restriction = 1
            elif self.ssk_alpha < self.cone_opening_angle_right:
                self.ssk_alpha = self.cone_opening_angle_right
                restriction = -1

            self.alpha = self.shift_alpha + self.ssk_alpha

            self.query_data["alpha"] = {}
            self.query_data["alpha"]["value"] = self.alpha
            self.query_data["alpha"]["restriction"] = restriction

        if "distance" in self.query:
            self.point_x = self.x + self.max_range * cos(self.alpha)
            self.point_y = self.y + self.max_range * sin(self.alpha)

            result = self.method(
                (self.x, self.y), (self.point_x, self.point_y), **self.method_kwargs
            )

            if result:
                self.point_x, self.point_y = result
                distance = sqrt(
                    (self.x - self.point_x) ** 2 + (self.y - self.point_y) ** 2
                )
                self.measurement = True
            else:
                distance = self.max_range
                self.measurement = False

            self.point_x_ssk = distance * cos(self.ssk_alpha)
            self.point_y_ssk = distance * sin(self.ssk_alpha)

            self.query_data["distance"] = {}
            self.query_data["distance"]["x"] = self.point_x
            self.query_data["distance"]["y"] = self.point_y
            self.query_data["distance"]["measurement"] = self.measurement

            self.query_data["distance"]["ssk_x"] = self.point_x
            self.query_data["distance"]["ssk_y"] = self.point_y
            self.query_data["distance"]["value"] = distance


class Locator(SightingSystem):
    def __init__(self, name, config: str | dict):
        self.required_fields = {
            "min_range",
            "max_range",
            "max_angle_speed",
            "zero",
            "cone_opening_angle",
            "ray_count",
            "ray_step",
        }

        super().__init__(name, config)

    def _unpack_config(self, data):
        config = data.copy()

        config["max_angle_speed"] = config["max_angle_speed"]
        config["cone_opening_angle"] = config["cone_opening_angle"]
        config["ray_step"] = config["ray_step"]

        if self.required_fields - set(data.keys()):
            raise KeyError(
                f"incomplete config, {self.required_fields - config.keys()} not in config"
            )
        self.config = config

    def _load_config(self, filename):
        with open(filename, "r") as f:
            data = yaml.safe_load(f)["locator"]

        if len(self.required_fields - data.keys()) > 0:
            raise KeyError(
                f"incomplete config, {self.required_fields - data.keys()} not in config"
            )
        config = data
        # в файле конфига все в градусах -
        config["max_angle_speed"] = radians(config["max_angle_speed"])
        config["cone_opening_angle"] = radians(config["cone_opening_angle"])
        config["ray_step"] = radians(config["ray_step"])

        self.config = config

    def processing_query(self, query):
        if "config" in query:
            self.query_data["config"] = {
                name: getattr(self, name) for name in self.config.keys()
            }

        if "turn" in query:
            _delta = query["turn"] - self.alpha
            delta = sign(_delta) * min(self.max_angle_speed, abs(_delta))
            result = (
                self.alpha + delta
            )  # угол поврота отн строительной оси паравоза против - положительный

            min_angle = self.zero - self.cone_opening_angle
            max_angle = self.zero + self.cone_opening_angle

            if result < min_angle:
                result = min_angle
            elif result > max_angle:
                result = max_angle

            self.angle = result

        self.query_data["angle"] = self.angle

        if "distance" in query:
            x, y = self.coords
            x_pos, y_pos = self.place  # отн кооординаты точки посадки

            x_pos_alpha = x_pos * cos(self.ship_alpha) - y_pos * sin(self.ship_alpha)
            y_pos_alpha = x_pos * sin(self.ship_alpha) + y_pos * cos(self.ship_alpha)

            x_pos_abs = x_pos_alpha + x
            y_pos_abs = y_pos_alpha + y

            begin_angle = self.zero - (self.ray_count - 1) * self.ray_step / 2

            measurement = []
            self.query_data["measurement"] = {}

            for ray_num in range(self.ray_count):
                angle = self.ship_alpha + begin_angle * ray_num
                distance = self.max_range

                x_end = distance * cos(angle)
                y_end = distance * sin(angle)

                result = self.method(
                    (x_pos_abs, y_pos_abs), (x_end, y_end), **self.method_kwargs
                )

                # result (x, y) or None
                results = {}
                results["angle"] = angle
                if result:
                    x_, y_ = result
                    dist = sqrt((x_pos_abs - x_) ** 2 + (y_pos_abs - y_) ** 2)
                    results["distance"] = dist
                    results["obstacle"] = True
                else:
                    results["distance"] = self.max_range
                    results["obstacle"] = False

                measurement.append(results)

            self.query_data["measurement"] = measurement
