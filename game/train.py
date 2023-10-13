from math import cos, sin, radians
from random import uniform
from game.locator import Locator


class Train:

    def __init__(self,
                 x0: float,
                 y0: float,
                 alpha0: float,
                 v_max: float,
                 locator: Locator,
                 ):

        self.alpha = alpha0  # строительная ось от оси x против часовой стрелки
        self.x = x0
        self.y = y0

        self.v_max = v_max
        self.locator = locator

        self.v = 10
        self.shape = None
        self.distance = None
        self.oneturncount = 0
        self.turn = 1
        self.points = []
        self.auto = True

    def update(self, x: float, y: float):

        # TODO в будющих версиях боты сами будут счислять свое положение
        if self.auto:
            self.x = x
            self.y = y

        # дергаем измерение локатора
        measurement = self.locator.measurement

        if measurement['query']:
            x_q, y_q, alpha_q = measurement['query'][0]
            self.distance = measurement['distance']

            if self.distance:
                new_point = (
                    x_q + self.distance * cos(alpha_q),
                    y_q + self.distance * sin(alpha_q)
                )

                self.points.append(new_point)

        else:
            self.distance = None

    def info(self) -> dict:

        # TODO!
        color1 = (255, 0, 0)
        color2 = (0, 120, 0)
        color3 = (255, 0, 150)
        line1 = [(100, 200,), (100, 300), color1]
        line2 = [(150, 250), (150, 350), color2]
        line3 = [(0, 0), (500, 500), color3]
        circle1 = ((100, 200), 20, color3)  # (point, radius)
        circle2 = ((200, 400), 30, color3)  # (point, radius)
        circle3 = ((400, 600), 40, color2)  # (point, radius)

        figures = {
            "lines": [line1, line2, line3, ],  # не замкнутая
            "circles": [circle1, circle2, circle3],
            "points": self.points
        }

        return {
            "params": (self.x, self.y, self.v, self.alpha),
            "maps": figures
        }

    def processing(self):
        if self.auto:
            self.processing_auto()

    def manual_update(self, x: float, y: float, alpha: float):
        if not self.auto:
            self.x += x
            self.y += y
            self.alpha += alpha

        self.locator.make_query(self.x, self.y, self.alpha)

    def processing_auto(self):

        if self.distance:

            if self.distance <= 20:
                self.alpha = self.alpha + radians(180.0) + uniform(radians(-10.0), radians(10.0))

            elif self.distance < 400:
                self.alpha += radians(2.0) * self.turn
                self.oneturncount += 1

            if self.oneturncount > 100 and self.distance > 100:
                self.alpha = self.alpha + radians(90.0) * self.turn + uniform(radians(-10.0), radians(10.0))
                self.turn = -self.turn
                self.oneturncount = 0

        self.x += self.v * cos(self.alpha)
        self.y += self.v * sin(self.alpha)

        self.locator.make_query(self.x, self.y, self.alpha)
