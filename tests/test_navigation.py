from math import radians, cos, sin

from game.exceptions import ConfigError
from game.mathfunction import sign
from game.navigation import NavigationSystem

EPS = 1e-5


class RPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @property
    def point(self):
        return self.x, self.y


def test_creation():
    config = {
        "v_max": 20,  # максимальная скорость
        "max_angle_speed": 5,  # максимальная угловая скорость
    }
    navigation = NavigationSystem(0, 0, 0, config)
    assert navigation is not None


def test_config_invalid():
    config = {}

    try:
        NavigationSystem(0, 0, 0, config)
        assert False
    except ConfigError:
        assert True

    config = {
        "v_max": 20,
    }
    try:
        NavigationSystem(0, 0, 0, config)
        assert False
    except ConfigError:
        assert True

    config = {
        "max_angle_speed": 5,  # максимальная угловая скорость
    }
    try:
        NavigationSystem(0, 0, 0, config)
        assert False
    except ConfigError:
        assert True


def test_step_zero_without_collision():
    config = {
        "v_max": 10,  # максимальная скорость
        "max_angle_speed": radians(10),  # максимальная угловая скорость
    }

    methods = [
        lambda crd0, crd1, **kwargs: None,
        lambda crd0, crd1, **kwargs: RPoint(*crd1),
        lambda crd0, crd1, **kwargs: RPoint(*crd1),
    ]
    responses = [False, False, True]

    vel = [10, 0, 10]

    for method, responce, v in zip(methods, responses, vel):
        navigation = NavigationSystem(0, 0, 0, config)
        navigation.set_measurement_method(method)

        navigation.receive({"v": v, 'alpha': radians(0)})
        navigation.step()
        state = navigation.send()

        assert abs(state['x'] - v) < EPS
        assert abs(state['y'] - 0.0) < EPS
        assert abs(state['alpha'] - 0.0) < EPS
        assert state['collision'] is responce


def test_movements_math():
    configs = [
        {"v_max": 10, "max_angle_speed": radians(10), },
        {"v_max": 1000, "max_angle_speed": radians(360), },
    ]

    # нет коллизии

    methods = [lambda crd0, crd1, **kwargs: None, lambda crd0, crd1, **kwargs: RPoint(*crd1)]
    responces = [False, True]
    velosites = [0, 5, 10, 15]
    alphas = [0, radians(5), radians(-5), radians(-90), radians(90), radians(180)]
    x0, y0, alpha0 = 0, 0, 0

    for config in configs:
        for method, responce in zip(methods, responces):
            for velocity in velosites:
                for alpha in alphas:
                    navigation = NavigationSystem(x=x0, y=y0, alpha=alpha0, config=config)
                    navigation.set_measurement_method(method)

                    navigation.receive({"v": velocity, 'alpha': alpha})
                    navigation.step()
                    state = navigation.send()

                    correct_alpha = sign(state['alpha']) * min(abs(alpha - alpha0), config["max_angle_speed"])
                    correct_x = min(velocity, config["v_max"]) * cos(correct_alpha)
                    correct_y = min(velocity, config["v_max"]) * sin(correct_alpha)
                    assert abs(state['alpha'] - correct_alpha) < EPS
                    assert abs(state['x'] - correct_x) < EPS
                    assert abs(state['y'] - correct_y) < EPS
                    if velocity > EPS:
                        assert state['collision'] is responce
                    else:
                        assert state['collision'] is False
