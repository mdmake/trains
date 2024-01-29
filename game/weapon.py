from math import atan2, radians
from typing import Callable

from game.mathfunction import distanse2D
from game.navigation import NavigationMixin
from game.trainsystem import TrainSystem


class BaseWeapon(NavigationMixin, TrainSystem):

    def __init__(self, x, y, alpha, v, max_lifetime=float('inf')):
        self.alpha = alpha
        self.x = x
        self.y = y
        self.v = v

        self.lifetime = 0
        self.max_lifetime = max_lifetime
        self.alive = True

        self.collision = False

        self.method = None
        self.method_kwargs = {}

        self._new_v = v
        self.v_max = v
        self._new_alpha = alpha
        self.max_angle_speed = 0.0

    def set_measurement_method(self, method: Callable, **kwargs):
        self.method = method
        self.method_kwargs = kwargs


class Cannon(BaseWeapon):

    def update_navigation(self, x: float | int, y: float | int, alpha: float | int):
        pass

    def receive(self, query: dict):
        pass

    def step(self):
        self.lifetime += 1
        self.x, self.y, self.alpha, self.v, self.collision = self.step_restriction()

        if self.collision or self.lifetime > self.max_lifetime or not self.alive:
            self.alive = False

    def send(self) -> dict:
        """
        Посылка данных
        """
        return {
            'x': self.x,
            'y': self.y,
            'alpha': self.alpha,
            'alive': self.alive,
        }


class Rocket(BaseWeapon):

    def __init__(self, x, y, alpha, v, target_x, target_y):
        super().__init__(x, y, alpha, v)
        self.target_x, self.target_y = target_x, target_y
        self.max_angle_speed = radians(90.0)

    def update_navigation(self, x: float | int, y: float | int, alpha: float | int):
        pass

    def receive(self, query: dict):

        if 'target' in query:
            self.target_x = query['target']['x']
            self.target_y = query['target']['y']

    def step(self):
        self.lifetime += 1

        self._new_alpha = atan2(self.target_y - self.y, self.target_x - self.x)

        self.x, self.y, self.alpha, self.v, self.collision = self.step_restriction()

        if (
                self.collision or
                self.lifetime > self.max_lifetime or
                not self.alive or
                distanse2D((self.x, self.y), (self.target_x, self.target_y)) <= self.v
        ):
            self.alive = False

    def send(self) -> dict:
        """
        Посылка данных
        """
        return {
            'x': self.x,
            'y': self.y,
            'alpha': self.alpha,
            'alive': self.alive,
        }

    def update_target(self, x, y):
        self.target_x = x
        self.target_y = y
