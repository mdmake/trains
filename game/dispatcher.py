from math import radians, cos, sin
from typing import Callable

import pymunk

from game.cartographer import Cartographer
from game.navigation import NavigationSystem
from game.sightingsystem import Laser
from game.sightingsystem import Locator
from game.train import Train
from game.weapon import Cannon, Rocket


class TPlayer:
    def __init__(
        self,
        init_x: float | int,
        init_y: float | int,
        init_alpha: float | int,
        method: Callable,
        method_kwargs: dict,
    ):
        place = [5, 0]

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
            x=init_x, y=init_y, alpha=init_alpha, config=full_train_config["tth"]
        )
        self.navigation.set_measurement_method(method, **method_kwargs)

        self.laser = Laser("test_laser", full_laser_config)
        self.laser.set_measurement_method(method, **method_kwargs)

        self.locator = Locator("test_locator", full_locator_config)
        self.locator.set_measurement_method(method, **method_kwargs)

        self.cartographer = Cartographer()

        self.train = Train("test_locator", full_train_config)

        self.to_laser = {}
        self.to_locator = {}
        self.to_train = {}
        self.to_navigation = {"v": 0, "alpha": radians(0)}

        self.from_laser = {}
        self.from_locator = {}
        self.from_train = {}
        self.from_navigation = {}

        self.points = []

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

        self.points = []

        if self.from_locator:
            for point in self.from_locator["distance"]:
                if point["measurement"]:
                    self.points.append((point["x"], point["y"]))
        if self.from_laser:
            for point in self.from_laser["distance"]:
                if point["measurement"]:
                    self.points.append((point["x"], point["y"]))

        self.cartographer.append(self.points)
        # self.cartographer.update()

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
        position: tuple[float | int, float | int],
        angle: float,
        name: str = "Unknown Train",
        color: tuple[int] = (0, 0, 255)
    ):
        self.space = space

        self.name = name
        self.color = color
        self.train_shape = None

        self.map = set()

        method = self.space.segment_query_first
        method_kwargs = {"radius": 0.01, "shape_filter": pymunk.ShapeFilter()}
        self.train = TPlayer(position[0], position[1], angle, method, method_kwargs)
        self.create_shapes()
        self.bullets = []
        self.rockets = []

    def create_shapes(self):
        self.train_shape = pymunk.Poly(
            None, ((0.0, 0.0), (-15.0, -50.0), (15.0, -50.0))
        )
        train_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.train_shape.body = train_body
        train_body.angle = 0
        train_body.sensor = False

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

        # порождаем ракеты
        if "rocket" in self.train.from_train:
            fire_rocket = self.train.from_train["rocket"].get("fire_rocket", False)
        else:
            fire_rocket = False

        if fire_rocket:
            rocket = Rocket(
                x=self.train.from_navigation["x"],
                y=self.train.from_navigation["y"],
                alpha=self.train.from_navigation["alpha"],
                v=5,
                target_x=self.train.from_train["rocket"]["target"]["x"],
                target_y=self.train.from_train["rocket"]["target"]["y"],
            )

            rocket.set_measurement_method(
                self.space.segment_query_first,
                **{"radius": 0.01, "shape_filter": pymunk.ShapeFilter()},
            )

            self.rockets.append(rocket)
        self.rockets = [rocket for rocket in self.rockets if rocket.alive]

        for rocket in self.rockets:
            rocket.step()
            rocket.update_target(
                self.train.from_train["rocket"]["target"]["x"],
                self.train.from_train["rocket"]["target"]["y"],
            )

        # порождаем снаряды
        if "cannon" in self.train.from_train:
            fire_cannon = self.train.from_train["cannon"].get("fire_cannon", False)
        else:
            fire_cannon = False

        if fire_cannon:
            bullet = Cannon(
                x=self.train.from_navigation["x"],
                y=self.train.from_navigation["y"],
                alpha=self.train.from_navigation["alpha"],
                v=5,
                max_lifetime=30,
            )

            # method = self.space.segment_query_first
            # method_kwargs = {"radius": 0.01, "shape_filter": pymunk.ShapeFilter()}
            bullet.set_measurement_method(
                self.space.segment_query_first,
                **{"radius": 0.01, "shape_filter": pymunk.ShapeFilter()},
            )

            self.bullets.append(bullet)

        self.bullets = [bullet for bullet in self.bullets if bullet.alive]

        for bullet in self.bullets:
            bullet.step()

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
            "clusters": self.train.cartographer.clusters,
            "bullets": [bullet.send() for bullet in self.bullets],
            "rockets": [rocket.send() for rocket in self.rockets],
        }

        return data
