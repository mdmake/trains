import uuid
from math import cos, sin, radians
from random import uniform
from game.locator import Locator


class Train:

    def __init__(self, alpha, position, **arguments):

        self.id = uuid.uuid4()

        self.alpha = alpha  # строительная ось от оси x против часовой стрелки
        self.position = position
        self.v = 0

        self.name = None
        self.color = None

        self.v_max = arguments['max_speed']
        self.angle_speed_max = arguments['angle_speed_max']
        self.shape = arguments['shape']
        self.center = arguments['center']
        self.place = arguments['place']

        self.life = arguments['life']

        self.auto = True

        self.locator = None
        self.laser = None
        self.gun = None
        self.rocket = []

        self.navigator = None
        self.map = None
        self.cartographer = None
        self.trajectory = []

        self.touch = False

        self.points = []

    def set_description(self, name=None, color=None):
        self.name = name
        self.color = color


    def update(self, position, laser):

        self.position = position
        self.trajectory.append(self.position)

        measurement = self.laser.measurement
        x, y, alpha = measurement['query']

        if measurement:
            distance = measurement['distance']
            l_point = (x + distance * cos(alpha), y + distance * sin(alpha))
            self.cartographer.append(l_point)

        else:
            distance = self.laser.range
            l_point = (x + distance * cos(alpha), y + distance * sin(alpha))

        self.points.append(l_point)

        measurements = self.locator.measurement
        x, y = measurement['query']
        for measurement, alpha in measurements:
            if measurement:
                distance = measurement['distance']
                lc_point = (x + distance * cos(alpha), y + distance * sin(alpha))
                self.cartographer.append(lc_point)
            else:
                distance = self.locator.range
                lc_point = (x + distance * cos(alpha), y + distance * sin(alpha))

            self.points.append(lc_point)

    def info(self) -> dict:

        # TODO!
        figures = {
            "lines": [],  # не замкнутая
            "circles": [],
            "points": self.points
        }

        return {
            "params": (self.x, self.y, self.v, self.alpha),
            "maps": figures
        }

    def processing(self):
        pass
