import pymunk
from game.train import Train
from math import sqrt, radians
from game.locator import Locator
from collections import namedtuple


class UpdatedTrain(Train):

    def __init__(self,
                 x0: float,
                 y0: float,
                 alpha0: float,
                 v_max: float,
                 locator: Locator,
                 name: str = "Unknown Train",
                 color: tuple[int] = (0, 0, 255)
                 ):
        super().__init__(x0, y0, alpha0, v_max, locator)
        self.name = name
        self.color = color
        self.auto = False
        self.v = 0


class Dispatcher:

    def __init__(self):
        self.players = []

    def append(self, player=None, player_config=None):


        pass

    def step(self):
        pass


class Player:

    def __init__(self, *,
                 space: pymunk.Space,
                 position: tuple[float],
                 angle: float,
                 name: str = "Unknown Train",
                 color: tuple[int] = (0, 0, 255)
                 ):
        self.position = position
        self.angle = angle
        self.space = space
        self.ray_length = 100
        self.blind_zone = 5
        self.collision = None
        self.locator = Locator(self.ray_length, self.blind_zone)
        self.v_max = 10
        self.name = name
        self.train = UpdatedTrain(
            position[0],
            position[1],
            angle,
            self.v_max,
            self.locator,
            self.name,
            color)

        self.create_shapes()
        self.set_touchpoint_invisible()
        self.map = set()

    def create_shapes(self):
        ray_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        ray_shape = pymunk.Segment(ray_body, (0, self.blind_zone), (0, self.ray_length), 1)
        ray_body.position = self.position
        ray_body.angle = -self.angle
        ray_shape.color = (217, 34, 28, 255)
        ray_shape.sensor = True
        self.ray_body = ray_body
        self.space.add(self.ray_body, ray_shape)

        self.train_shape = pymunk.Poly(None, ((0.0, 0.0), (-15.0, -50.0), (15.0, -50.0)))
        train_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.train_shape.body = train_body
        train_body.angle = self.angle
        train_body.position = self.position
        train_body.sensor = False

        # train_shape.sensor = True
        self.train_shape.color = (*self.train.color, 255)
        self.train_body = train_body
        self.space.add(self.train_body, self.train_shape)

        end_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        end_shape = pymunk.Circle(end_body, 5)
        end_shape.color = (0, 0, 0, 0)
        end_body.position = self.position
        end_shape.sensor = True
        self.end_body = end_body
        self.end_shape = end_shape
        self.space.add(self.end_body, self.end_shape)

    def set_touchpoint_visible(self):
        # self.end_shape.color = (255, 0, 0, 255)
        pass

    def set_touchpoint_invisible(self):
        # self.end_shape.color = (0, 0, 0, 0)
        pass

    def make_query(self, query):

        # self._query = LocatorQuery((x, y, alpha), begin_point, end_point)
        if query:
            return self.space.segment_query_first(query[1], query[2], 0.1, pymunk.ShapeFilter())

    def update(self) -> dict[str, list]:
        # запрашиваем локатор
        collision = self.make_query(self.locator.query)

        if collision and collision.shape is not self.train_shape:
            # self.set_touchpoint_visible()
            # self.end_body.position = collision.pointqqq
            # print(f"{self.locator.query} ==> {collision.point}")

            point0 = self.locator.query[0][0:2]
            point1 = collision.point

            distance = sqrt(
                (point0[0] - point1[0]) ** 2 +
                (point0[1] - point1[1]) ** 2
            )
        else:
            print(f"{self.locator.query} ==> None")
            self.set_touchpoint_invisible()
            distance = None

        self.locator._set_distance(distance)

        # запускаем бот
        self.train.update(*self.position)
        self.train.processing()
        info = self.train.info()

        # меняем позицию на экране
        self.position = info['params'][0], info['params'][1]
        self.angle = info['params'][3]
        self.train_body.angle = self.angle - radians(90)
        self.train_body.position = self.position

        data = {
            "points": info['maps']['points'],
            "lines": info['maps']['lines'],
            "circles": info['maps']['circles'],
        }

        return data
