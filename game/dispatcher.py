from math import radians, cos, sin

import pymunk

from game.navigation import NavigationSystem
from game.sightingsystem import Laser
from game.sightingsystem import Locator
from game.train import Train


class TPlayer:
    def __init__(self, method, method_kwargs):
        place = [5, 15]

        full_train_config = {
            "tth": {
                "v_max": 20,
                "max_angle_speed": radians(30),
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

        self.navigation = NavigationSystem(
            x=700, y=400, alpha=radians(0), config=full_train_config["tth"]
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
        method_kwargs = {"radius": 0.01, "shape_filter": pymunk.ShapeFilter()}
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

    def prepare_laser_lines(self, vs: Laser | Locator, vs_data: dict):
        laser_lines = {}
        laser_lines["restrictions"] = {}
        laser_lines["restrictions"]["lines"] = []
        laser_lines["restrictions"]["arcs"] = []

        left_res = vs.ship_alpha + vs.shift_alpha + vs.cone_opening_angle_left
        right_res = vs.ship_alpha + vs.shift_alpha + vs.cone_opening_angle_right

        laser_res_x = vs.x + vs.max_range * cos(left_res)
        laser_res_y = vs.y + vs.max_range * sin(left_res)

        laser_lines["restrictions"]["lines"].append(
            ((vs.x, vs.y), (laser_res_x, laser_res_y))
        )

        laser_res_x = vs.x + vs.max_range * cos(right_res)
        laser_res_y = vs.y + vs.max_range * sin(right_res)

        laser_lines["restrictions"]["lines"].append(
            ((vs.x, vs.y), (laser_res_x, laser_res_y))
        )

        laser_lines["restrictions"]["arcs"].append(
            (
                vs.x,
                vs.y,
                vs.max_range,
                2 * vs.cone_opening_angle_left,
                right_res,
            )
        )

        laser_lines["ray"] = []
        laser_lines["measurement"] = []
        if "distance" in vs_data:
            for ray in vs_data["distance"]:
                laser_lines["ray"].append(
                    (
                        (vs.x, vs.y),
                        (
                            ray["x"],
                            ray["y"],
                        ),
                    )
                )
                laser_lines["measurement"].append(ray["measurement"])

        if "alpha" in vs_data:
            laser_lines["alpha_restriction"] = vs_data["alpha"]["restriction"]
        else:
            laser_lines["alpha_restriction"] = 0

        return laser_lines

    def step(self) -> dict[str, list]:
        # запрашиваем локатор

        self.train.step()

        self.train_body.angle = self.train.navigation.alpha - radians(90)
        self.train_body.position = self.train.navigation.x, self.train.navigation.y

        lines = []
        arcs = []

        laser_lines = self.prepare_laser_lines(self.train.laser, self.train.from_laser)
        locator_lines = self.prepare_laser_lines(
            self.train.locator, self.train.from_locator
        )

        data = {
            "points": [
                (self.train.locator.x, self.train.locator.y),
                (self.train.laser.x, self.train.laser.y),
            ],
            "lines": lines,
            "circles": [],
            "arcs": arcs,
            "laser": laser_lines,
            "locator": locator_lines,
        }

        return data
