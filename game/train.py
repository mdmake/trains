import uuid
from math import cos, sin, radians
from random import uniform
from game.locator import Locator
from game.interfaces import LocatorInterface, LaserInterface


class Train:

    def __init__(self, alpha, position, **arguments):

        self.id = uuid.uuid4()

        self.alpha = alpha  # строительная ось от оси x против часовой стрелки
        self.position = position
        self.v = 0

        self.laser = LaserInterface()

        self.locator = LocatorInterface()

        self.laser.get_config()
        self.locator.get_config()

        self.ready = False
        self.laser_config = None
        self.locator_config = None

    def set_description(self, name=None, color=None):
        self.name = name
        self.color = color

    def update(self, position, laser):

        if not self.ready:
            if not self.laser_config:
                self.laser_config = self.laser.config
            if not self.locator_config:
                self.locator_config = self.locator.config

            self.ready = self.laser_config and self.locator_config
        else:
            pass

    def info(self):

        pass

    def processing(self):

        if self.laser_config and self.locator_config:
            pass
        else:
            pass

