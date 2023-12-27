from math import radians

from game.navigation import NavigationSystem
from game.sightingsystem import Laser, Locator
from game.train import Train

place = [5, 15]

full_train_config = {
    "tth": {"v_max": 20, "max_angle_speed": 5, },
    "private": {"place": place}
}

full_laser_config = {
    "min_range": 0,
    "max_range": 100,
    "max_angle_speed": radians(5),
    "cone_opening_angle": radians(150),
    "zero": radians(10),
    "place": place,
    "fire_power": 100,
    "fire_time_limit": 5,
    "max_angle_speed_tracking": radians(4),
}

full_locator_config = {
    "min_range": 5,
    "max_range": 40,
    "max_angle_speed": radians(2),
    "cone_opening_angle": radians(120),
    "zero": radians(0),
    "place": place,
    "ray_count": 11,
    "ray_step": 6,
}

method = lambda crd0, crd1, **kwargs: None


class Player:
    def __init__(self):
        self.navigation = NavigationSystem(x=0, y=0, alpha=0, config=full_train_config['tth'])
        self.navigation.set_measurement_method(method)

        self.laser = Laser("test_laser", full_laser_config)
        self.laser.set_measurement_method(method)

        self.locator = Locator("test_locator", full_locator_config)
        self.locator.set_measurement_method(method)

        self.train = Train("test_locator", full_train_config)

        self.to_laser = {}
        self.to_locator = {}
        self.to_train = {}
        self.to_navigation = {"v": 0, 'alpha': radians(0)}

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

        self.to_train['laser'] = self.from_laser
        self.to_train['locator'] = self.from_locator

        self.train.update_navigation(**self.from_navigation)
        self.train.receive(self.to_train)
        self.train.step()
        self.from_train = self.train.send()

        self.to_navigation = self.from_train['navigation']
        self.to_locator = self.from_train['locator']
        self.to_laser = self.from_train['laser']


def test_system_creation():
    player = Player()

    for _ in range(10):
        player.step()

    assert True
