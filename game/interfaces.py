class SightingSystemInterface:
    def __init__(self):
        self.query_data = {}
        self.data = {}
        self.angle = None  # угол относительно строительной оси, плюс -- направо
        self.coords = None  # координаты xy относительно строительной оси
        self.measurement = None  # словарь - id, дальность, пересечение
        self.config = None

    def take_measurement(self):
        # просим померить дальность
        self.query_data['distance'] = True

    def turn(self, angle):
        # просим повернуть датчик
        self.query_data['angle'] = angle

    def get_config(self):
        # просим отдать конфиг
        self.query_data['config'] = True

    def send_query(self):
        """
        набираем запрос и посылаем его, обнуляем запрос
        """
        q = self.query_data
        self.query_data = {}
        return q

    def input(self, data):
        """
        кладем в интерфейс сырые данные
        """
        self.data = data


class LocatorInterface(SightingSystemInterface):
    def set_data(self, data):
        self.data = data

        self.angle = self.data.get('angle')
        self.coords = self.data.get('coords')
        self.timestamp = self.data['timestamp']

        if "measurement" in self.data:
            self.measurement = {}
            self.measurement['distances'] = self.data['measurement']['distances']
            self.measurement['obstacles'] = self.data['measurement']['obstacles']
        else:
            self.measurement = None

        if "config" in self.data:
            self.config["name"] = self.data["name"]
            self.config["min_range"] = self.data["min_range"]
            self.config["max_range"] = self.data["max_range"]
            self.config["zero"] = self.data["zero"]  # установочный угол относительно строительной оси
            self.config["cone_opening_angle"] = self.data["cone_opening_angle"]  # угол раскрыва конуса
            self.config["ray_count"] = self.data["ray_count"]
            self.config["ray_angle_position"] = self.data["ray_angle_position"]


class LaserInterface(SightingSystemInterface):

    def tracking(self, state=True):
        self.query_data['tracking'] = state

    def fire(self, state=False):
        self.query_data['fire'] = state

    def set_data(self, data):
        self.data = data

        self.angle = self.data.get('angle')
        self.coords = self.data.get('coords')
        self.timestamp = self.data['timestamp']
        self.tracking = self.data['tracking']

        if "measurement" in self.data:
            self.measurement = {}
            self.measurement['distance'] = self.data['measurement']['distance']
            self.measurement['obstacle'] = self.data['measurement']['obstacle']
        else:
            self.measurement = None

        if "config" in self.data:
            self.config["name"] = self.data["name"]
            self.config["min_range"] = self.data["min_range"]
            self.config["max_range"] = self.data["max_range"]
            self.config["zero"] = self.data["zero"]  # установочный угол относительно строительной оси
            self.config["cone_opening_angle"] = self.data["cone_opening_angle"]  # угол раскрыва ограничивающего конуса
