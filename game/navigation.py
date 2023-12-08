from math import sin, cos, radians
from typing import Tuple
from .mathfunction import sign
import yaml


class NavigationSystem:

    def __init__(self, x, y, angle, config):
        self.x = x
        self.y = y
        self.angle = angle

        self.method = None
        self.method_kwargs = None

        if isinstance(config, dict):
            self.config = self._unpack_config(config)
        else:
            self.config = self._load_config(config)

        self.v_max = self.config['v_max']
        self.max_angle_speed = self.config['max_angle_speed']
        self.collision = False

    def _unpack_config(self, data):
        config = data.copy()
        config["max_angle_speed"] = config["max_angle_speed"]
        config["v_max"] = config["cone_opening_angle"]
        return config

    def _load_config(self, filename):
        config = {}
        with open(filename, 'r') as f:
            data = yaml.safe_load(f)['train']['tth']

            config["max_angle_speed"] = radians(data["max_angle_speed"])
            config["v_max"] = radians(data["cone_opening_angle"])

        return config

    def set_measurement_method(self, method, **kwargs):
        self.method = method
        self.method_kwargs = kwargs

    def step_restriction(self, alpha, v) -> tuple[tuple[float, float], bool]:

        v = min(v, self.v_max)
        alpha = sign(alpha) * min(alpha, self.max_angle_speed)

        x = self.x + v * cos(alpha)
        y = self.y + v * sin(alpha)

        result = self.method((self.x, self.y), (x, y), **self.method_kwargs)
        if result:
            x, y = result
            return (x, y), False
        return (x, y), True

    def step(self, alpha, v):
        (x, y), self.collision = self.step_restriction(alpha, v)
        return x, y
