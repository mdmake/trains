from math import radians, cos, sin

import pymunk

from game.navigation import NavigationSystem
from game.sightingsystem import Laser
from game.sightingsystem import Locator
from game.train import Train

place = [5, 0]

full_train_config = {
    "tth": {
        "v_max": 20,
        "max_angle_speed": 5,
    },
    "private": {"place": place},
}

full_laser_config = {
    "min_range": 0,
    "max_range": 300,
    "max_angle_speed": radians(5),
    "cone_opening_angle": radians(120),
    "zero": radians(10),
    "place": place,
    "fire_power": 100,
    "fire_time_limit": 5,
    "max_angle_speed_tracking": radians(4),
}

full_locator_config = {
    "min_range": 5,
    "max_range": 150,
    "max_angle_speed": radians(5),
    "cone_opening_angle": radians(120),
    "zero": radians(0),
    "place": place,
    "ray_count": 11,
    "ray_step": radians(5),
}


class TPlayer:
    def __init__(self, method, method_kwargs):
        self.navigation = NavigationSystem(
            x=600, y=300, alpha=radians(0), config=full_train_config["tth"]
        )
        self.navigation.set_measurement_method(method, **method_kwargs)

        self.laser = Laser("test_laser", full_laser_config)
        self.laser.set_measurement_method(method, **method_kwargs)

        self.locator = Locator("test_locator", full_locator_config)
        self.locator.set_measurement_method(method, **method_kwargs)

        self.train = Train("test_locator", full_train_config)

        self.to_laser = {}
        self.to_locator = {}
        self.to_train = {}
        self.to_navigation = {"v": 0, "alpha": radians(0)}

        self.from_laser = {}
        self.from_locator = {}
        self.from_train = {}
        self.from_navigation = {}

    def step(self):
        self.navigation.receive(self.to_navigation)
        self.navigation.step()
        self.from_navigation = self.navigation.send()

        self.from_navigation.pop("collision")

        self.laser.update_navigation(**self.from_navigation)
        self.laser.receive(self.to_laser)
        self.laser.step()
        self.from_laser = self.laser.send()

        self.locator.update_navigation(**self.from_navigation)
        self.locator.receive(self.to_locator)
        self.locator.step()
        self.from_locator = self.locator.send()

        self.to_train["laser"] = self.from_laser
        self.to_train["locator"] = self.from_locator

        self.train.update_navigation(**self.from_navigation)
        self.train.receive(self.to_train)
        self.train.step()
        self.from_train = self.train.send()

        self.to_navigation = self.from_train["navigation"]
        self.to_locator = self.from_train["locator"]
        self.to_laser = self.from_train["laser"]


class Player:
    def __init__(
            self,
            *,
            space: pymunk.Space,
            position: tuple[float],
            angle: float,
            name: str = "Unknown Train",
            color: tuple[int] = (0, 0, 255)
    ):
        self.space = space

        self.v_max = 10
        self.name = name
        self.color = color

        self.map = set()

        method = self.space.segment_query_first
        method_kwargs = {"radius": 0.1, "shape_filter": pymunk.ShapeFilter()}
        self.train = TPlayer(method, method_kwargs)
        self.create_shapes()

    def create_shapes(self):
        self.train_shape = pymunk.Poly(
            None, ((0.0, 0.0), (-15.0, -50.0), (15.0, -50.0))
        )
        train_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.train_shape.body = train_body
        train_body.angle = self.train.navigation.alpha
        train_body.position = self.train.navigation.x, self.train.navigation.y
        train_body.sensor = False

        # train_shape.sensor = True
        self.train_shape.color = (*self.color, 255)
        self.train_body = train_body
        self.space.add(self.train_body, self.train_shape)

    def step(self) -> dict[str, list]:
        # запрашиваем локатор

        self.train.step()

        self.train_body.angle = self.train.navigation.alpha - radians(90)
        self.train_body.position = self.train.navigation.x, self.train.navigation.y

        lines = []

        left_res = self.train.laser.ship_alpha + self.train.laser.shift_alpha + self.train.laser.cone_opening_angle_left
        right_res = self.train.laser.ship_alpha + self.train.laser.shift_alpha + self.train.laser.cone_opening_angle_right

        laser_res_x = self.train.laser.x + self.train.laser.max_range * cos(left_res)
        laser_res_y = self.train.laser.y + self.train.laser.max_range * sin(left_res)
        lines.append(((self.train.laser.x, self.train.laser.y), (laser_res_x, laser_res_y)))

        laser_res_x = self.train.laser.x + self.train.laser.max_range * cos(right_res)
        laser_res_y = self.train.laser.y + self.train.laser.max_range * sin(right_res)
        lines.append(((self.train.laser.x, self.train.laser.y), (laser_res_x, laser_res_y)))

        left_res = self.train.locator.ship_alpha + self.train.locator.shift_alpha + self.train.locator.cone_opening_angle_left
        right_res = self.train.locator.ship_alpha + self.train.locator.shift_alpha + self.train.locator.cone_opening_angle_right

        locator_res_x = self.train.locator.x + self.train.locator.max_range * cos(left_res)
        locator_res_y = self.train.locator.y + self.train.locator.max_range * sin(left_res)
        lines.append(((self.train.locator.x, self.train.locator.y), (locator_res_x, locator_res_y)))

        locator_res_x = self.train.locator.x + self.train.locator.max_range * cos(right_res)
        locator_res_y = self.train.locator.y + self.train.locator.max_range * sin(right_res)
        lines.append(((self.train.locator.x, self.train.locator.y), (locator_res_x, locator_res_y)))

        if "distance" in self.train.from_laser:
            lines.append(
                (
                    (self.train.laser.x, self.train.laser.y),
                    (
                        self.train.from_laser["distance"]["x"],
                        self.train.from_laser["distance"]["y"],
                    ),
                )
            )

        if "distance" in self.train.from_locator:
            for item in self.train.from_locator["distance"]:
                lines.append(
                    (
                        (self.train.locator.x, self.train.locator.y),
                        (item["x"], item["y"]),
                    )
                )

        data = {
            "points": [
                (self.train.locator.x, self.train.locator.y),
                (self.train.laser.x, self.train.laser.y),
            ],
            "lines": lines,
            "circles": [],
        }

        return data
