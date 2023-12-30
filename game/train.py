import uuid
from copy import deepcopy
from math import radians, remainder, tau

import yaml

from game.trainsystem import TrainSystem


class Train(TrainSystem):
    def __init__(self, name: str, config: str | dict):
        self.id = uuid.uuid4()

        self.alpha = None
        self.x = None
        self.y = None
        self.v = 0

        self.name = name
        self.query_data = {}
        self.query = {}

        if isinstance(config, dict):
            self._unpack_config(config)
        else:
            self._load_config(config)

        self.v_max = self.config["tth"]["v_max"]
        self.place = self.config["private"]["place"]

        self.locator_alpha = 0
        self.laser_alpha = 0

        self.auto = True
        self.memory = None

    def _unpack_config(self, data: dict):
        self.config = data.copy()

        self.max_angle_speed = self.config["tth"]["max_angle_speed"]

    def _load_config(self, filename: str):
        with open(filename, "r") as f:
            self.config = yaml.safe_load(f)["train"]

        self.max_angle_speed = radians(self.config["tth"]["max_angle_speed"])

    def update_navigation(self, x: float | int, y: float | int, alpha: float | int):
        """
        Обновление навигационной информации

        :param x: координата x борта в абсолютной СК
        :param y: координата y борта в абсолютной СК
        :param alpha: угол поворота в абсолютной СК от оси х, против часовой стрелки
        """
        self.x = x
        self.y = y
        self.alpha = alpha

    def send(self) -> dict:
        return self.query_data

    def receive(self, query: dict):
        self.query = deepcopy(query)

    def step(self):
        if self.auto:
            self.locator_alpha = remainder(self.locator_alpha + radians(1), tau)
            self.laser_alpha = remainder(self.laser_alpha, tau)

            self.alpha = remainder(self.alpha + radians(5), tau)
            self.v = 4

            self.query_data = {"locator": {}}
            self.query_data["locator"]["turn"] = self.locator_alpha
            self.query_data["locator"]["distance"] = True

            self.query_data["laser"] = {}
            self.query_data["laser"]["turn"] = self.laser_alpha
            self.query_data["laser"]["distance"] = True

            self.query_data["navigation"] = {}
            self.query_data["navigation"]["v"] = self.v
            self.query_data["navigation"]["alpha"] = self.alpha

        else:
            self.locator_alpha = remainder(self.locator_alpha + radians(1), tau)
            self.laser_alpha = remainder(self.alpha, tau)

            self.alpha = remainder(self.alpha + self.memory.get("delta_alpha", 0), tau)
            self.v = max(self.v + self.memory.get("delta_v", 0), 0)

            self.query_data = {"locator": {}}
            self.query_data["locator"]["turn"] = self.locator_alpha
            self.query_data["locator"]["distance"] = True

            self.query_data["laser"] = {}
            self.query_data["laser"]["turn"] = self.laser_alpha
            self.query_data["laser"]["distance"] = True

            self.query_data["navigation"] = {}
            self.query_data["navigation"]["v"] = self.v
            self.query_data["navigation"]["alpha"] = self.alpha

            self.memory = {}

    def external(self, **kwargs: dict):
        """
        Эту функцию можно вызвать снаружи и положить в нее управление. После того как
        управление будет отработано, self.memory надо почистить
        """
        self.memory = {
            "delta_alpha": remainder(kwargs.get("alpha", 0), tau),
            "delta_v": kwargs.get("v", 0),
        }
