import yaml
from math import radians, cos, sin, sqrt
from .mathfunction import sign


class SightingSystem:
    def __init__(self, name, config: str | dict):

        self.name = name

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

    def _unpack_config(self, data):
        raise NotImplementedError

    def _load_config(self, data):
        raise NotImplementedError

    def set_measurement_method(self, method, **kwargs):
        self.method = method
        self.method_kwargs = kwargs

    def update(self, coords, ship_angle):
        self.coords = coords
        self.ship_angle = ship_angle

    def send_query(self):
        return self.query_data


class Laser(SightingSystem):
    def __init__(self, name, config: str | dict):

        self.required_fields = {
            "min_range", "max_range", "max_angle_speed",
            "zero", "fire_power", "cone_opening_angle",
            "fire_time_limit", "max_angle_speed_tracking"
        }

        super().__init__(name, config)

    def _unpack_config(self, data):

        config = data.copy()

        config["max_angle_speed"] = config["max_angle_speed"]
        config["cone_opening_angle"] = config["cone_opening_angle"]
        config["max_angle_speed_tracking"] = config["max_angle_speed_tracking"]

        if self.required_fields - config.keys():
            raise KeyError(f"incomplete config, {self.required_fields - config.keys()} not in config")
        return config

    def _load_config(self, filename):
        with open(filename, 'r') as f:
            data = yaml.safe_load(f)['laser']

        if self.required_fields - data.keys():
            raise KeyError(f"incomplete config, {self.required_fields - data.keys()} not in config")
        config = data
        # в файле конфига все в градусах -
        config["max_angle_speed"] = radians(config["max_angle_speed"])
        config["cone_opening_angle"] = radians(config["cone_opening_angle"])
        config["max_angle_speed_tracking"] = radians(config["max_angle_speed_tracking"])

        return config

    def processing_query(self, query):

        if "config" in query:
            self.query_data['config'] = {
                name: getattr(self, name) for name in self.config.keys()
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


class Locator(SightingSystem):
    def __init__(self, name, config: str | dict):

        self.required_fields = {
            "min_range", "max_range", "max_angle_speed",
            "zero", "cone_opening_angle",
            "ray_count", "ray_step"
        }

        super().__init__(name, config)

    def _unpack_config(self, data):

        config = data.copy()

        config["max_angle_speed"] = config["max_angle_speed"]
        config["cone_opening_angle"] = config["cone_opening_angle"]
        config["ray_step"] = config["ray_step"]

        if self.required_fields - set(data.keys()):
            raise KeyError(f"incomplete config, {self.required_fields - config.keys()} not in config")
        return config

    def _load_config(self, filename):
        with open(filename, 'r') as f:
            data = yaml.safe_load(f)['locator']

        if len(self.required_fields - data.keys()) > 0:
            raise KeyError(f"incomplete config, {self.required_fields - data.keys()} not in config")
        config = data
        # в файле конфига все в градусах -
        config["max_angle_speed"] = radians(config["max_angle_speed"])
        config["cone_opening_angle"] = radians(config["cone_opening_angle"])
        config["ray_step"] = radians(config["ray_step"])

        return config

    def processing_query(self, query):

        if "config" in query:
            self.query_data['config'] = {
                name: getattr(self, name) for name in self.config.keys()
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

            begin_angle = self.zero - (self.ray_count - 1) * self.ray_step / 2

            measurement = []
            self.query_data['measurement'] = {}

            for ray_num in range(self.ray_count):

                angle = self.ship_angle + begin_angle * ray_num
                distance = self.max_range

                x_end = distance * cos(angle)
                y_end = distance * sin(angle)

                result = self.method((x_pos_abs, y_pos_abs), (x_end, y_end), **self.method_kwargs)

                # result (x, y) or None
                results = {}
                results['angle'] = angle
                if result:
                    x_, y_ = result
                    dist = sqrt((x_pos_abs - x_) ** 2 + (y_pos_abs - y_) ** 2)
                    results['distance'] = dist
                    results['obstacle'] = True
                else:
                    results['distance'] = self.max_range
                    results['obstacle'] = False

                measurement.append(results)

            self.query_data['measurement'] = measurement
