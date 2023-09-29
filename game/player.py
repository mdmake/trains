import pyglet
import pymunk
from game.train import Train
from math import sin, cos, sqrt, radians


class UpdatedTrain(Train):

    def __init__(self, x0, y0, alpha0, name="Unknown Train"):
        super().__init__(x0, y0, alpha0)
        self.name = name
        self.v = 0


class Player:

    def __init__(self, *, space, position, angle):
        self.position = position
        self.angle = angle
        self.space = space
        self.ray_length = 450
        self.create_shapes()
        self.set_touchpoint_invisible()
        self.train = UpdatedTrain(*position, angle)

    def create_shapes(self):
        ray_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        ray_shape = pymunk.Segment(ray_body, (0, 0), (0, self.ray_length), 1)
        ray_body.position = self.position
        ray_body.angle = -self.angle
        ray_shape.color = (217, 34, 28, 255)
        ray_shape.sensor = True
        self.ray_body = ray_body
        self.space.add(self.ray_body, ray_shape)

        train_shape = pymunk.Poly(None, ((0.0, 0.0), (-15.0, -50.0), (15.0, -50.0)))
        train_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        train_body.position = 200, 200
        train_shape.body = train_body
        train_body.angle = ray_body.angle
        train_body.position = ray_body.position
        train_shape.sensor = True
        train_shape.color = (34, 98, 201, 255)
        self.train_body = train_body
        self.space.add(self.train_body, train_shape)

        end_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        end_shape = pymunk.Circle(end_body, 3)
        end_shape.color = (0, 0, 0, 0)
        end_body.position = self.position
        end_shape.sensor = True
        self.end_body = end_body
        self.end_shape = end_shape
        self.space.add(self.end_body, self.end_shape)

    def set_touchpoint_visible(self):
        self.end_shape.color = (217, 200, 28, 255)

    def set_touchpoint_invisible(self):
        self.end_shape.color = (0, 0, 0, 0)

    def make_query(self):
        new_point = (
            self.position[0] + self.ray_length * cos(self.angle),
            self.position[1] + self.ray_length * sin(self.angle))
        return self.space.segment_query_first(self.position, new_point, 0.01, pymunk.ShapeFilter())

    def update(self):
        distance = None
        collision = self.make_query()

        if collision:
            self.set_touchpoint_visible()

            self.end_body.position = collision.point

            distance = sqrt(
                (collision.point[0] - self.position[0]) ** 2 +
                (collision.point[1] - self.position[1]) ** 2
            )
        else:
            self.set_touchpoint_invisible()

        self.train.update(*self.position, distance)
        self.train.processing()
        info = self.train.info()

        self.position = info['params'][0], info['params'][1]
        self.angle = info['params'][3]

        self.ray_body.angle = self.angle - radians(90)
        self.ray_body.position = self.position
        self.train_body.angle = self.ray_body.angle
        self.train_body.position = self.ray_body.position

        return info
