import yaml
import datetime
import os
from geometry.geometry import Point, Circle, Rectangle, Border


class Map:
    """
    Класс "Карта".
    """

    def __init__(self, path: str | None = None):
        """
        Инициализация объекта карты.

        :param path: Путь к файлу с картой.
        """

        self.__description = dict()
        self.__complete = 0
        self.__circles = dict()
        self.__rectangles = dict()
        self.__border = dict()
        self.__path = path or self.set_default_path()

    @property
    def is_complete(self) -> bool:
        """
        Проверка на завершенность карты.

        :return: True, если карта завершена более чем на 90%, иначе - False.
        """

        return True if self.__complete > 95 else False

    @property
    def description(self) -> dict:
        """
        :return: Описание к карте.
        """

        return self.__description

    @property
    def complete(self) -> float:
        """
        :return: Завершенность карты в процентах.
        """

        return self.__complete

    @property
    def border(self) -> dict:
        """
        :return: Словарь с информацией о границе поля.
        """

        return self.__border

    @property
    def circles(self) -> dict:
        """
        :return: Словарь с информацией об объектах поля.
        """

        return self.__circles

    @property
    def rectangles(self) -> dict:
        """
        :return: Словарь с информацией об объектах поля.
        """

        return self.__rectangles

    @property
    def path(self) -> str:
        """
        :return: Путь к файлу в виде строки.
        """

        return self.__path

    @staticmethod
    def set_default_path() -> str:
        """
        Установка дефолтного пути к файлу с картой.

        :return: Дефолтный путь к новоиспеченному файлу.
        """

        base = 'FlyingLocomotivesMap'
        counter = 0

        while True:
            current_name = f'{base}{counter}.yaml' if counter > 0 else f'{base}.yaml'

            if os.path.exists(current_name):
                counter += 1
            else:
                return current_name

    @staticmethod
    def represent_list(dumper, data):
        """
        Функция, представляющая список (list) в файле .yaml в одной строке с квадратными скобками. Например,
        список **[[100, 100], [100, 250], [250, 250], [250, 100]]** в файле .yaml будет отображаться абсолютно также,
        как представлен здесь.
        """

        return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)

    def load(self, path: str | None = None) -> None:
        """
        Чтение карты из файла (формат .yaml).

        :param path: Путь к файлу.
        :return: None.
        """

        with open(path or self.__path or self.set_default_path(), 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)

            if 'description' not in data.keys():
                self.__description = {
                    'map_name': 'DEFAULT_NAME',
                    'date': datetime.datetime.today().strftime("%H:%M:%S %d.%m.%Y"),
                    'text': 'DEFAULT_TEXT',
                    'complete': 0
                }
            else:
                self.__description = data['description']

            self.__complete = self.__description['complete']

            if 'border' not in data.keys():
                self.__border = []
            else:
                self.__border = data['border']

            if 'circles' not in data.keys():
                self.__circles = data['circles']
            else:
                self.__circles = data['circles']

            if 'rectangles' not in data.keys():
                self.__rectangles = []
            else:
                self.__rectangles = data['rectangles']

    def save(self, path: str | None = None, map_name: str | None = None, text: str | None = None) -> None:
        """
        Запись карты в файл (формат .yaml).

        :param path: Путь к файлу.
        :param map_name: Название карты.
        :param text: Описание.
        :return: None.
        """

        self.__description['date'] = datetime.datetime.today().strftime("%H:%M:%S %d.%m.%Y")
        self.__description['map_name'] = map_name or self.__description.get('map_name', 'Default')
        self.__description['text'] = text or self.__description.get('text', 'Default')

        with open(path or self.__path, 'w', encoding='utf-8') as file:
            data = dict(
                {
                    "description": self.__description,
                    "border": self.__border,
                    "circles": self.__circles,
                    "rectangles": self.__rectangles
                }
            )

            yaml.add_representer(list, self.represent_list)

            yaml.dump(
                data=data,
                stream=file,
                sort_keys=False,
                allow_unicode=True,
                indent=4,
            )

    def add_object(self, obj: Circle | Rectangle | Border) -> bool:
        """
        Добавление объектов в карту.

        :param obj: Объект, который может быть: Окружностью, Прямоугольником или Границей.
        :return: True, если объект успешно добавлен в карту, иначе - False.
        """

        if obj.object_type not in ('border', 'circle', 'rectangle'):
            return False

        if obj.object_type == 'circle':
            last_obj_name = list(self.__circles.keys())[-1]
        elif obj.object_type == 'rectangle':
            last_obj_name = list(self.__rectangles.keys())[-1]
        else:
            last_obj_name = obj.object_type

        current_obj_name = 'border' if obj.object_type == 'border' \
            else f"{obj.object_type}_{str(int(last_obj_name.split('_')[1]) + 1)}"

        # Если тип рассматриваемого объекта является "границей"
        if obj.object_type == 'border' and not self.__border:
            self.__border = [list(obj.border.rectangle[i].angle[1].point) for i in range(4)]

        # Если тип рассматриваемого объекта является "окружностью"
        if obj.object_type == 'circle':
            for circle in self.__circles:
                current = self.__circles[circle]

                if obj == Circle(Point(current['center'][0], current['center'][1]), current['radius']):
                    return False

            self.__circles[current_obj_name] = {
                'center': list(obj.center.point),
                'radius': obj.radius
            }

        # Если тип рассматриваемого объекта является "прямоугольником"
        if obj.object_type == 'rectangle':
            for rectangle in self.__rectangles:
                current = self.rectangles[rectangle]['coordinates']

                for point in current:
                    for angle in obj.rectangle:
                        if Point(*point) == angle.angle[1]:
                            return False

            self.__rectangles[current_obj_name] = {
                'coordinates': [list(obj.rectangle[i].angle[1].point) for i in range(4)]
            }

        return True


if __name__ == '__main__':
    mapp = Map('field_1.yaml')
    mapp.load()
    print(mapp.rectangles)