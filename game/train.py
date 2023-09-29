from math import cos, sin, radians
from random import uniform


class Train:

    def __init__(self, x0, y0, alpha0):
        self.alpha = alpha0  # строительная ось от оси x против часовой стрелки
        self.x = x0
        self.y = y0
        self.v = 10
        self.shape = None
        self.distance = None
        self.oneturncount = 0
        self.turn = 1
        self.maps = []

    def update(self, x, y, distance=None):
        self.distance = distance
        self.x = x
        self.y = y

    def info(self):
        # do something

        return {
            "params": (self.x, self.y, self.v, self.alpha),
            "maps": self.maps
        }

    def processing(self):

        if self.distance:

            if self.distance <= 20:
                self.alpha = self.alpha + radians(180.0) + uniform(radians(-10.0), radians(10.0))

            elif self.distance < 400:
                new_point = self.x + self.distance * cos(self.alpha), self.y + self.distance * sin(self.alpha)
                self.maps.append(new_point)
                self.alpha += radians(2.0) * self.turn
                self.oneturncount += 1

            if self.oneturncount > 100 and self.distance > 100:
                self.alpha = self.alpha + radians(90.0) * self.turn + uniform(radians(-10.0), radians(10.0))
                self.turn = -self.turn
                self.oneturncount = 0

        self.x += self.v * cos(self.alpha)
        self.y += self.v * sin(self.alpha)
