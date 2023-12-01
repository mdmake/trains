import yaml
from math import radians, cos, sin, sqrt


def sign(x):
    return 1 if x >= 0 else -1


class Laser:
    def __init__(self, name, config: str | dict):
        self.name = name
        self.required_fields = {
            "min_range", "max_range", "max_angle_speed",
            "zero", "fire_power", "cone_opening_angle",
            "fire_time_limit", "max_angle_speed_tracking"
        }

        if isinstance(config, dict):
            self.config = self._unpack_config(config)
        else:
            self.config = self._load_config(config)

        for name, value in self.config.items():
            setattr(self, name, value)

        self.method_kwargs = None
        self.method = None
        self.coords = None
        self.ship_angle = None
        self.angle = 0
        self.query_data = {}
        self.place = (0, 20)

    def set_measurment_method(self, method, **kwargs):
        self.method = method
        self.method_kwargs = kwargs

    def _unpack_config(self, data):

        config = data.copy()

        config["max_angle_speed"] = radians(config["max_angle_speed"])
        config["cone_opening_angle"] = radians(config["cone_opening_angle"])
        config["max_angle_speed_tracking"] = radians(config["max_angle_speed_tracking"])

        if self.required_fields not in data:
            raise KeyError(f"incomplete config, {self.required_fields - config.keys()} not in config")
        return config

    def _load_config(self, filename):
        with open(filename, 'r') as f:
            data = yaml.safe_load(f)['laser']

        if len(self.required_fields - data.keys()) > 0:
            raise KeyError(f"incomplete config, {self.required_fields - data.keys()} not in config")
        config = data
        # в файле конфига все в градусах -
        config["max_angle_speed"] = radians(config["max_angle_speed"])
        config["cone_opening_angle"] = radians(config["cone_opening_angle"])

        return config

    def update(self, coords, ship_angle):
        self.coords = coords
        self.ship_angle = ship_angle

    def processing_query(self, query):

        if "config" in query:
            self.query_data['config'] = {
                getattr(self, name) for name in self.config.keys()
            }

        if "turn" in query:
            _delta = query['turn'] - self.angle
            delta = sign(_delta) * min(self.max_angle_speed, abs(_delta))
            result = self.angle + delta  # угол поврота отн строительной оси паравоза против - положительный

            min_angle = self.zero - self.cone_opening_angle
            max_angle = self.zero + self.cone_opening_angle

            if result < min_angle:
                result = min_angle
            elif result > max_angle:
                result = max_angle

            self.angle = result

        self.query_data['angle'] = self.angle

        if "distance" in query:
            x, y = self.coords
            x_pos, y_pos = self.place  # отн кооординаты точки посадки

            x_pos_alpha = x_pos * cos(self.ship_angle) - y_pos * sin(self.ship_angle)
            y_pos_alpha = x_pos * sin(self.ship_angle) + y_pos * cos(self.ship_angle)

            x_pos_abs = x_pos_alpha + x
            y_pos_abs = y_pos_alpha + y

            distance = self.max_range
            angle = self.ship_angle + self.angle

            x_end = distance * cos(angle)
            y_end = distance * sin(angle)

            result = self.method((x_pos_abs, y_pos_abs), (x_end, y_end), **self.method_kwargs)

            # result (x, y) or None

            self.query_data['measurement'] = {}

            if result:
                x_, y_ = result
                dist = sqrt((x_pos_abs - x_) ** 2 + (y_pos_abs - y_) ** 2)

                self.query_data['measurement']['distance'] = dist
                self.query_data['measurement']['obstacle'] = True
            else:
                self.query_data['measurement']['distance'] = self.max_range
                self.query_data['measurement']['obstacle'] = False

        if "fire" in query:
            raise NotImplementedError

        if "tracking" in query:
            raise NotImplementedError

    def send_query(self):
        return self.query_data.deepcopy()
