import math
import numpy as np
import sympy

TOLERANCE = 3

class Geometry:
    def __init__(self, color: tuple[int, int, int] = (0, 0, 0), object_type: str | None = None, **kwargs):
        self.__color = color
        self.__square = 0
        # TODO
        self.__object_type = object_type


    @property
    def object_type(self) -> str | None:
        return self.__object_type

    def set_color(self, color: tuple[int, int, int]):
        pass

    def square(self):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError


class Point(Geometry):
    """
    Класс "Точка".
    """

    def __init__(self, x: float, y: float, color: tuple[int, int, int] = (0, 0, 255)):
        super().__init__(color=color, object_type='point')
        self.__x = x
        self.__y = y
        # self.__neighbors = []

    def __eq__(self, other: 'Point') -> bool:
        """
        Проверка совпадения точек по расстоянию между ними с некоторой погрешностью.

        :param other: Точка (объект класса Point).
        :return: True, если расстояние между точками меньше некоторого значения, иначе - False.
        """

        return True if self.distance(other) < TOLERANCE else False

    def almost_eq(self, other: 'Point', tol=TOLERANCE):
        pass

    def __hash__(self):
        return hash(self.__point)

    # line + point = line
    # line - point = line
    # point +point = line

    def __add__(self, other: 'Point') -> 'Line':
        """
        Объединение двух точек (объекты класса Point) в прямую (объект класса Line). Например, line = point_1 + point_2.

        :param other: Точка (объект класса Point).
        :return: прямая (объект класса Line).
        """
        return Line(start=self, end=other)

    @property
    def x(self) -> float:
        """
        Получение абсциссы (координата X) точки.

        :return: Значение абсциссы -> (координата X).
        """

        return self.__x

    @property
    def y(self) -> float:
        """
        Получение ординаты (координата Y) точки.

        :return: Значение ординаты -> (координата Y).
        """

        return self.__y

    @property
    def point(self) -> tuple[float, float]:
        """
        Получение точки в виде кортежа из ее абсциссы (координата X) и ординаты (координата Y).

        :return: Кортеж координат -> (координата X, координата Y).
        """
        return self.__x, self.__y


    def distance(self, other: 'Point') -> float:
        """
        Получение расстояния между точками.

        :param other: Другая точка (объект класса Point), расстояние до которой нужно вычислить.
        :return: Расстояние между точками.
        """

        return math.sqrt((other.x - self.__x) ** 2 + (other.y - self.__y) ** 2)

    # def __contains__(self, item): для линии
    # TODO ????
    def is_in_list(self, points: list['Point']) -> bool:
        """
        Проверка наличия точки в списке точек.

        :param points: Список объектов класса Point.
        :return: True, если точка есть в списке points, иначе - False.
        """

        for other in points:
            # TODO
            # if self.distance(other) < 3:
            # TODO
            # if self.distance(other) < TOLERANCE:
            if self == other:
                return True

        return False


class Line(Geometry):
    """
    Класс "Прямая".
    """

    def __init__(self, start: Point, end: Point, color: tuple[int, int, int] = (255, 0, 0)):
        super().__init__(color=color, object_type='line')
        self.__start = start
        self.__end = end

        self.get_sorted_points()

    @property
    def line(self):
        return self.__start, self.__end

    def __eq__(self, other: 'Line'):
        return self.line == other.line


    def is_it_possible_to_merge_the_lines(self, other: 'Line'):
        # TODO -- ahtung!!!
        # угол ---
        if 'x' in self.line_equation.keys() and 'x' in self.line_equation.keys():
            if self.__start.y <= other.start.y <= self.__end.y or self.__start.y <= other.end.y <= self.__end.y:
                return True
        elif 'y' in self.line_equation.keys() and 'y' in self.line_equation.keys():
            if self.__start.x <= other.start.x <= self.__end.x or self.__start.x <= other.end.x <= self.__end.x:
                return True
        else:
            if self.__start.x <= other.start.x <= self.__end.x or self.__start.x <= other.end.x <= self.__end.x:
                return True
        return False

    def merge_the_lines(self, other: 'Line') -> 'Line' or None:
        if self.are_equations_the_same(other=other):
            if self.is_it_possible_to_merge_the_lines(other=other):
                return self.get_new_line(other=other)


    def __str__(self):
        """
        Выдача человекочитаемой информации о прямой и срединном перпендикуляре к ней.

        :return: 3 строки с информацией:
                    1) точки, через которые проходит прямая;
                    2) уравнение прямой;
                    3) уравнение срединного перпендикуляра.
        """

        result = [f'Прямая проходит через две точки --> '
                  f'P1{(self.__start.x, self.__start.y)}, P2{(self.__end.x, self.__end.y)}\n']

        if 'x' in self.__line_equation.keys():
            result.append({'equation': f'x = {self.__line_equation["x"]}'})
        elif 'y' in self.__line_equation.keys():
            result.append({'equation': f'y = {self.__line_equation["y"]}'})
        else:
            k = self.__line_equation['k']
            b = self.__line_equation['b']
            result.append({'equation': f'y = {k} x {f"+ {b}" if b > 0 else b}'})

        if 'x' in self.__median_perpendicular_equation.keys():
            result.append({'equation': f'x = {self.__median_perpendicular_equation["x"]}'})
        elif 'y' in self.__median_perpendicular_equation.keys():
            result.append({'equation': f'y = {self.__median_perpendicular_equation["y"]}'})
        else:
            k = self.__median_perpendicular_equation['k']
            b = self.__median_perpendicular_equation['b']
            result.append({'equation': f'y = {k} x {f"+ {b}" if b > 0 else b}'})

        return f'{result[0]}' \
               f'Уравнение прямой --> {result[1]["equation"]}\n' \
               f'Уравнение срединного перпендикуляра к прямой --> {result[2]["equation"]}'


    @property
    def median_point(self) -> Point:
        """
        Возвращает кортеж координат середины отрезка (координата X, координата Y).
        """

        return Point((self.__start.x + self.__end.x) / 2, (self.__start.y + self.__end.y) / 2)

    @property
    def line_equation(self):
        """
        Возвращает уравнение прямой.
        """

        return self.__line_equation

    @property
    def median_perpendicular_equation(self):
        """
        Возвращает уравнение срединного перпендикуляра к прямой.
        """

        if 'x' in self.__line_equation.keys():
            return {'y': self.__median_point.y}
        elif 'y' in self.__line_equation.keys():
            return {'x': self.__median_point.x}
        else:
            k = - 1 / self.__line_equation['k']
            b = (self.__median_point.x / self.__line_equation['k']) + self.__median_point.y

            return {'k': k, 'b': b}


    @property
    def line_equation(self) -> dict:
        """
        Вычисление коэффициентов прямой.

        :return: Коэффициенты прямой k и b или уравнение вида x=Const/y=Const.
        """

        artan = math.atan2(self.__end.y - self.__start.y, self.__end.x - self.__start.x)

        if math.pi / 2 - 0.1 < math.fabs(artan) < math.pi / 2 + 0.1:
            return {'x': self.__start.x}
        elif - 0.1 < math.fabs(artan) < 0.1 or math.pi - 0.1 < math.fabs(artan) < math.pi + 0.1:
            return {'y': self.__start.y}
        else:
            return {'k': math.tan(artan), 'b': self.__start.y - math.tan(artan) * self.__start.x}


    # TODO
    def get_intersection(self, other: 'Line', median_perpendicular=False) -> Point | None:
        """
        Определение точки пересечения двух прямых.

        :param other: Другая прямая (объект класса Line).
        :param median_perpendicular: Флаг, определяющий уравнение самой прямой или ее срединного перпендикуляра.
        :return: Точка пересечения (), в противном случае -> None.
        """
        # TODO

        return Point(x_result, y_result) if x_result and y_result else None

    # TODO ANG_TOL = 0.1
    def is_perpendicular(self, other: 'Line') -> bool:
        return (math.pi / 2) - 0.1 < self.angle_between_lines(other) < (math.pi / 2) + 0.1

    # TODO -- plus , minus, other  -- может __add__, __sub__, по другому реализовать?
    # TODO pow
    # угол между линиями
    def angle_between_lines(self, other: 'Line'):
        vec1 = (self.__end.x - self.__start.x, self.__end.y - self.__start.y)
        vec2 = (other.end.x - other.start.x, other.end.y - other.start.y)

        numerator = vec1[0] * vec2[0] + vec1[1] * vec2[1]
        denominator = pow(pow(vec1[0], 2) + pow(vec1[1], 2), 0.5) * pow(pow(vec2[0], 2) + pow(vec2[1], 2), 0.5)

        # TODO
        # try:
        #     return math.fabs(math.acos(numerator / denominator))
        # except ZeroDivisionError:
        #     raise
        #     print(f'прямая {self.__line[0].point, self.__line[1].point} и {other.line[0].point, other.line[1].point}')

        # ЭТОТ СПОСОБ ПОЧЕМУ ТО НЕ РАБОТАЕТ:
        # slope1 = math.tan(math.atan2(self.__end.y - self.__start.y, self.__end.y - self.__start.y))
        # slope2 = math.tan(math.atan2(other.end.y - other.start.y, other.end.y - other.start.y))
        #
        # return math.atan2(abs(slope2 - slope1), abs(1 + slope1 * slope2))

    # TODO лежат ли точки одной прямой на другой прямой
    # TODO Fix
    def are_equations_the_same(self, other: 'Line') -> bool:
        """
        Проверка, что уравнения двух прямых совпадают (с погрешностью).
        [(])

        {} []
        :param other: Объект второй прямой.
        :return: True, если уравнения совпадают, False - в противном случае.
        """
        if 'k' in self.line_equation.keys() and 'k' in other.line_equation.keys():
            if math.fabs(self.line_equation['k'] - other.line_equation['k']) < 3 and \
                    math.fabs(self.line_equation['b'] - other.line_equation['b']) < 50:
                return True
        elif 'x' in self.line_equation.keys() and 'x' in other.line_equation.keys():
            if math.fabs(self.line_equation['x'] - other.line_equation['x']) < 3:
                return True
        elif 'y' in self.line_equation.keys() and 'y' in other.line_equation.keys():
            if math.fabs(self.line_equation['y'] - other.line_equation['y']) < 3:
                return True

        return False

    # TODO нейминг, если она вспомогательная -- __
    def get_points_of_new_line(self, other: 'Line', mode: int, is_the_slope_positive=False):
        """
        Получение точек новой прямой.

        :param other: Другая прямая.
        :param mode: Режим, значение которого зависит от уравнения прямых.
        :param is_the_slope_positive: Флаг, который говорит возрастающей или убывающей прямой.
        :return: Объединенная прямая.
        """
        if mode not in (0, 1, 2):
            return

        line = None

        if mode == 0:
            max_x = max(self.__start.x, self.__end.x, other.start.x, other.end.x)
            max_y = max(self.__start.y, self.__end.y, other.start.y, other.end.y)
            min_x = min(self.__start.x, self.__end.x, other.start.x, other.end.x)
            min_y = min(self.__start.y, self.__end.y, other.start.y, other.end.y)

            if is_the_slope_positive:
                line = Point(min_x, min_y) + Point(max_x, max_y)
            else:
                line = Point(min_x, max_y) + Point(max_x, min_y)
        elif mode == 1:
            max_y = max(self.__start.y, self.__end.y, other.start.y, other.end.y)
            min_y = min(self.__start.y, self.__end.y, other.start.y, other.end.y)
            x = other.start.x
            line = Point(x, min_y) + Point(x, max_y)

        elif mode == 2:
            max_x = max(self.__start.x, self.__end.x, other.start.x, other.end.x)
            min_x = min(self.__start.x, self.__end.x, other.start.x, other.end.x)
            y = other.start.y
            line = Point(min_x, y) + Point(max_x, y)

        return line

    # TODO ну камон - 2:
    def get_new_line(self, other: 'Line'):
        mode = -1

        if 'k' in self.line_equation.keys() and 'k' in other.line_equation.keys():
            mode = 0
            is_positive = True if self.line_equation['k'] > 0 else False
            return self.get_points_of_new_line(other, mode, is_positive) if mode != -1 else None
        elif 'x' in self.line_equation.keys() and 'x' in other.line_equation.keys():
            mode = 1
        elif 'y' in self.line_equation.keys() and 'y' in other.line_equation.keys():
            mode = 2

        return self.get_points_of_new_line(other, mode) if mode != -1 else None

    # TODO на угол поменяйте!!!
    def is_oppositely_directed(self, other: 'Line'):
        vec1 = (self.__start.x - self.__end.x, self.__start.y - self.__end.y)
        vec2 = (other.start.x - other.end.x, other.start.y - other.end.y)

        return all(-0.8 < vec1[i] - vec2[i] < -1.2 for i in range(len(vec1)))


class StraightAngle(Geometry):
    """
    Класс "Прямой угол"
    """

    def __init__(self, line1: Line, intersection: Point, line2: Line, color: tuple[int, int, int] = (0, 255, 0)):
        self.__first_line = line1
        self.__second_line = line2

        self.__intersection_point = intersection
        self.__straight_angle = (line1, intersection, line2)
        # self.__neighbours = []

        self._is_convex = None

        super().__init__(color=color, object_type='angle')
        self.set_color(color)

    # TODO --
    def __hash__(self):
        return hash(self.__straight_angle[1])

    # TODO так все углы равны
    def __eq__(self, other: 'StraightAngle'):
        return self.__straight_angle[1] == other.angle[1]

    def set_color(self, value: tuple[int, int, int]):
        self.__first_line.color = value
        self.__second_line.color = value


    # TODO
    @property
    def first_line(self) -> Line:
        return self.__first_line

    @property
    def second_line(self) -> Line:
        return self.__second_line

    @property
    def angle(self):
        """

        :return:
        """
        return self.__straight_angle

    @property
    def is_convex(self) -> bool:
        """

        :return:
        """
        return self._is_convex

    def convex_or_concave_angle(self, train_position: Point):
        """
        Проверка и установка выпуклости/вогнутости прямого угла препятствия.

        :param train_position: Координаты позиции поезда.
        :return: None.
        """
        angle = self.__straight_angle

        far_far_away = [
            angle[0].start if angle[1].distance(angle[0].start) > angle[1].distance(angle[0].end) else angle[0].end,
            angle[2].start if angle[1].distance(angle[2].start) > angle[1].distance(angle[2].end) else angle[2].end
        ]

        main = far_far_away[0] + far_far_away[1]
        other = train_position + angle[1]
        inter = main.get_intersection(other)

        if inter.distance(train_position) > angle[1].distance(train_position):
            # Выпуклый угол
            print('Выпуклый!!!')
            self._is_convex = True
        else:
            # Вогнутый угол
            print('!!!Вогнутый')
            self._is_convex = False


class Circle(Geometry):
    """
    Класс "Окружность"
    """

    def __init__(self, center: Point, radius: float, color: tuple[int, int, int] = (0, 0, 0)):
        # TODO
        self.__circle = (center, radius)
        self.__center = center
        self.__radius = radius
        self.__square = 0
        self.__points_on_it = []

        self.calculating_the_square()
        super().__init__(color=color, object_type='circle')
        self.set_color(color)
        # print(f'Площадь окружности: {self.__square}')

    # TODO TOL
    def __contains__(self, point: Point):
        """
        Проверка точки на ее принадлежность окружности.

        :param point: Рассматриваемая точка.
        :return: True, если точка лежит в/на окружности, иначе - False.
        """

        return self.__center.distance(point) < self.__radius + 1

    # TODO -- ну это не отвали откровенно
    # def __hash__(self):
    #     return hash(self.__center, self.__radius)

    # TODO почему теперь один?
    def __eq__(self, other: 'Circle'):
        """
        Проверка эквивалентности окружностей.

        :param other: Другая окружность, с которой сравнивается текущая.
        :return: True, если окружности эквивалентны, иначе - False.
        """

        return self.__center.distance(other.center) < 1 and abs(self.__radius - other.__radius) < TOLERANCE

    def set_color(self, color: tuple[int, int, int]):
        """
        Установка цвета для окружности.

        :param color: Цвет в RGB палитре. Например, (255, 255, 255).
        :return: None.
        """

        self.center.color = color

    @property
    def square(self):
        return math.pi * self.__radius ** 2


    # def calculating_the_square(self):
    #     """
    #     Вычисление площади круга.
    #     """
    #
    #     self.__square = math.pi * self.__radius ** 2

    @property
    def points_on_it(self) -> list[Point]:
        """
        Получение точек, принадлежащих окружности.
        """

        return self.__points_on_it

    @property
    def circle(self) -> tuple[Point, float]:
        """
        Получение окружности.

        :return: Окружность в виде кортежа, состоящего из центра окружности (0-й элемент, объект класса Point (Точка))
                 и радиуса (1-й элемент (float))
        """

        return self.__circle

    @property
    def center(self) -> Point:
        """
        Получение координат центра окружности.

        :return: Центр окружности в виде объекта класса Point (Точка).
        """

        return self.__center

    @property
    def radius(self) -> float:
        """
        Получение радиуса окружности.

        :return: Радиус окружности.
        """

        return self.__radius

    # def is_exist(self, circles: list['Circle']) -> bool:
    #     """
    #     Проверка на существование окружности в списке окружностей.
    #
    #     :param circles: Рассматриваемая окружность.
    #     :return: True, если окружность существует, иначе - False.
    #     """
    #
    #     for circle in circles:
    #         other = Circle(center=Point(circle.center.x, circle.center.y), radius=circle.radius)
    #         if self.center.distance(other.__center) < other.radius:
    #             return True
    #
    #     return False


class Rectangle(Geometry):

    # TODO
    def __init__(self, rectangle: list[Point], color=(0, 0, 0), object_type: str = 'rectangle'):
        self.__rectangle: list[Point] = rectangle
        self.__center: Point | None = None
        self.__square: float = 0
        self.__larger_rectangle_points: list[Point] = []

        super().__init__(color=color, object_type=object_type)

        self.set_color(color=color)
        self.calculating_the_center()
        self.get_points_of_larger_rectangle(epsilon=10)
        self.sorting_vertices()
        self.calculating_the_square()

        # TODO
        # for top in self.__rectangle:
        #     print(top.point, end=', ')
        #
        # if self.object_type == 'border':
        #     print(f'Площадь поля: {self.__square}')
        # else:
        #     print(f'Площадь прямоугольника: {self.__square}')

    # TODO лежит внутри или на границе?
    def __contains__(self, point: Point):
        """
        Проверка точки на ее принадлежность прямоугольнику.

        :param point: Точка, которую необходимо проверить.
        :return: True, если точка лежит в/на прямоугольнике, иначе - False.
        """

        # rectangle = self.__larger_rectangle_points
        rectangle = self.__larger_rectangle_points

        sign = None

        print('***')
        for i in range(4):
            side_vector = np.array([
                rectangle[(i + 1) % 4].x - rectangle[i].x,
                rectangle[(i + 1) % 4].y - rectangle[i].y
            ])

            to_point_vector = np.array([point.x - rectangle[i].x, point.y - rectangle[i].y])

            if not sign:
                sign = np.dot(side_vector, to_point_vector) < 0
                print(f'sign: {sign} 1')
            else:
                if sign != (np.dot(side_vector, to_point_vector) < 0):
                    print(f'sign: {sign} 2')
                    print('***')
                    return False
        print('***')
        return True

    # def __eq__(self, other: 'Rectangle'):
    #     for self_point in self.__rectangle:
    #         for other_point in other.rectangle:
    #             if self_point == other_point:
    #                 return True
    #
    #     return False

    ###############
    # ДЛЯ ОТЛАДКИ #
    ###############
    # TODO
    @property
    def larger_rectangle_points(self):
        return self.__larger_rectangle_points

    @property
    def center(self) -> Point:
        """
        Получение центра прямоугольника.

        :return: объекта класса Point (Точка).
        """
        return self.__center

    @property
    def rectangle(self):
        """
        Получение списка из 4х прямых углов, составляющих прямоугольник.

        :return: list[StraightAngle].
        """
        return self.__rectangle

    @property
    def sides(self) -> list[Line]:
        """
        Получение сторон прямоугольника.
        """
        return [self.__rectangle[(i + 1) % 4] + self.__rectangle[i] for i in range(len(self.__rectangle))]

    def set_color(self, color):
        """
        Установка цвета для прямоугольника.

        :param color: Цвет, представленный в RGB палитре. Например, (255, 255, 255).
        :return: None.
        """
        for top in self.__rectangle:
            top.color = color

    def calculating_the_center(self):
        """
        Вычисление центра прямоугольника.

        :return: None.
        """
        center_x = sum(top.x for top in self.__rectangle)
        center_y = sum(top.y for top in self.__rectangle)

        self.__center = Point(center_x / 4, center_y / 4)

    def sorting_vertices(self):
        """
        Сортировка вершин прямоугольника. В итоге, вершины идут против часовой стрелки относительно центра
        прямоугольника.

        :return: None.
        """

        # TODO O(n2)
        for i in range(len(self.__rectangle)):
            for j in range(len(self.__rectangle)):

                artan1 = math.atan2(
                    self.__rectangle[i].y - self.__center.y,
                    self.__rectangle[i].x - self.__center.x
                )

                artan2 = math.atan2(
                    self.__rectangle[j].y - self.__center.y,
                    self.__rectangle[j].x - self.__center.x
                )
                if artan1 < artan2:
                    self.__rectangle[i], self.__rectangle[j] = self.__rectangle[j], self.__rectangle[i]

    def calculating_the_square(self):
        """
        Вычисление площади прямоугольника.

        :return: None.
        """
        a = self.__rectangle[0].distance(self.__rectangle[1])
        b = self.__rectangle[1].distance(self.__rectangle[2])
        self.__square = a * b

    def get_points_of_larger_rectangle(self, epsilon: float = 0.5):
        """
        Вычисление координат прямоугольника, большего, чем этот на величину epsilon.

        :param epsilon: Величина, на которую новый прямоугольник будет больше этого.
        :return: None.
        """
        # TODO point, corner
        for top in self.__rectangle:
            x, y = top.x, top.y
            # x = top.x
            # y = top.y

            dx = x - self.__center.x
            dy = y - self.__center.y

            new_dx = epsilon * math.cos(math.atan2(dy, dx))
            new_dy = epsilon * math.sin(math.atan2(dy, dx))

            self.__larger_rectangle_points.append(Point(x + new_dx, y + new_dy))


class Border(Rectangle):
    """
    Класс "Граница"
    """

    def __init__(self, border: Rectangle, color: tuple[int, int, int] = (255, 0, 247)):
        super().__init__(rectangle=border.rectangle, color=color, object_type='border')
        self.__border = border

    def __contains__(self, point):
        for top in self.__border.rectangle:
            if math.fabs(point.x - top.x) < 1 or math.fabs(point.y - top.y) < 1:
                return True
        return False

    @property
    def border(self) -> Rectangle:
        return self.__border


class Figures:
    """
    Класс "Фигуры"
    """

    def __init__(self, circles: list[Circle], rectangles: list[Rectangle], all_points):
        self.graph_points = all_points
        self.graph_lines = []
        self.__points: list[Point] = []
        self.__lines: list[Line] = []
        self.__straight_angles: list[StraightAngle] = []
        self.__circles: list[Circle] = circles
        self.__rectangles: list[Rectangle] = rectangles
        self.__border: Border | None = None

        self.get_tra()

        self.__field_boundary: list[StraightAngle] = []
        self.__groups_straight_angles: dict[StraightAngle, list[StraightAngle]] = dict()

    def get_tra(self):
        for point in self.graph_points:
            print(point)
            for neighbour in self.graph_points[point]:
                self.graph_lines.append(point + neighbour)

    @property
    def points(self) -> list[Point]:
        """
        Получение списка точек (список объектов класса Point).
        """

        return self.__points

    @property
    def lines(self) -> list[Line]:
        return self.__lines

    @property
    def straight_angles(self) -> list[StraightAngle]:
        return self.__straight_angles

    @property
    def circles(self) -> list[Circle]:
        return self.__circles

    @property
    def field_boundaries(self):
        return self.__field_boundary

    @property
    def rectangles(self) -> list[Rectangle]:
        return self.__rectangles

    @property
    def border(self) -> Border:
        return self.__border

    def __contains__(self, local_points: list[Point]):
        for point in local_points:
            # если точка находится на/в окружности:
            for circle in self.__circles:
                if point in circle:
                    return True

            # если точка находится на/в прямоугольнике:
            for rectangle in self.__rectangles:
                if point in rectangle:
                    return True

            # если точка находится на границе:
            # if self.__border and point in self.__border:
            #     return True

    def get_figures(self, local_points: list[Point], train_position: Point):
        if local_points in self:
            return False

        return self.get_angle(local_points, train_position) or \
            self.get_rectangle() or \
            self.get_line(local_points) or \
            self.get_circle(local_points)

    def is_point_on_the_border(self, point: Point) -> bool:
        if self.__border:
            for i in range(len(self.__field_boundary)):
                if point.is_on_line(self.__field_boundary[i].angle[0]):
                    return True

        return False

    def is_point_on_circle(self, local_point: Point) -> bool:
        for circle in self.__circles:
            if circle.center.distance(local_point) < circle.radius + 3:
                return True
        return False

    def check(self):
        if self.__lines:
            i = 0
            j = 0

            while i < len(self.__lines):
                current_line = self.__lines[i]

                while j < len(self.__lines):
                    if i == j:
                        j += 1
                        continue

                    next_line = self.__lines[j]

                    if current_line == next_line:
                        j += 1
                        continue

                    buffer = current_line.merge_the_lines(other=next_line)

                    if buffer:
                        self.__lines[j] = buffer
                        self.__lines.pop(i)
                        continue
                    else:
                        j += 1

                i += 1
                j = 0

    def get_line(self, queue_of_points: list[Point]) -> bool:
        is_line = False

        for i in range(2):
            if queue_of_points[i] == queue_of_points[i + 1]:
                return is_line

            if queue_of_points[i].distance(queue_of_points[i + 1]) > 50:
                return is_line

            if queue_of_points[i + 1].distance(queue_of_points[i + 1]) > 50:
                return is_line

            main = queue_of_points[i] + queue_of_points[i + 1]
            other = queue_of_points[i] + queue_of_points[i + 2]
            current_line = None

            if 'k' in main.line_equation.keys() and 'k' in other.line_equation.keys():
                equation1 = main.line_equation
                equation2 = other.line_equation

                tangent = (equation2['k'] - equation1['k']) / (1 + equation2['k'] * equation1['k'])

                if math.fabs(math.atan(tangent)) < 0.01:
                    current_line = other

            elif 'x' in main.line_equation.keys() and 'x' in other.line_equation.keys():
                if math.fabs(main.line_equation['x'] - other.line_equation['x']) < 2:
                    current_line = other

            elif 'y' in main.line_equation.keys() and 'y' in other.line_equation.keys():
                if math.fabs(main.line_equation['y'] - other.line_equation['y']) < 2:
                    current_line = other

            if self.__lines:
                if current_line:
                    j = 0
                    is_one_line = False

                    while j < len(self.__lines):
                        next_line = self.__lines[j]

                        if current_line == next_line:
                            j += 1
                            continue

                        buffer = current_line.merge_the_lines(other=next_line)

                        if buffer:
                            is_line = True
                            is_one_line = True
                            self.__lines[j] = buffer

                            break

                        j += 1

                    if not is_one_line:
                        is_line = True
                        self.__lines.append(current_line)
            else:
                if current_line:
                    is_line = True
                    self.__lines.append(current_line)

        self.check()

        # print(len(self.__lines))

        return is_line

    def get_angle(self, local_points: list[Point], train_position: Point) -> bool:
        is_angle = False

        if local_points[0].is_exist([local_points[1], local_points[2], local_points[3]]):
            return is_angle

        distances = [
            local_points[i].distance(local_points[i + 1]) for i in range(len(local_points) - 1)
        ]

        for i in range(len(distances)):
            if distances[i] > 50:
                return is_angle

        main_line = local_points[1] + local_points[0]

        other_line = local_points[2] + local_points[3]

        if 'k' in main_line.line_equation.keys() and 'k' in other_line.line_equation.keys():
            equation1 = main_line.line_equation
            equation2 = other_line.line_equation

            tangent = (equation2['k'] - equation1['k']) / (1 + equation2['k'] * equation1['k'])

            if 1.5 < math.fabs(math.atan(tangent)) < 1.6:
                is_angle = True

        elif 'x' in main_line.line_equation.keys() and 'y' in other_line.line_equation.keys():
            is_angle = True

        elif 'y' in main_line.line_equation.keys() and 'x' in other_line.line_equation.keys():
            is_angle = True

        if is_angle:
            point = main_line.get_intersection(other_line)

            first = main_line.end + point
            second = other_line.end + point

            straight_angle = StraightAngle(first, point, second)
            straight_angle.convex_or_concave_angle(train_position=train_position)

            if straight_angle.is_convex:
                if not straight_angle.is_exist(self.__straight_angles):
                    self.__straight_angles.append(straight_angle)
                    print(f'Выпуклый прямой угол!')
                else:
                    print(f'Выпуклый прямой угол существует!')
                    return False
            else:
                if not self.__border and not straight_angle.is_exist(self.__field_boundary):
                    print(f'Вогнутый прямой угол!')
                    self.__field_boundary.append(straight_angle)
                    self.get_field_boundaries()
                else:
                    print(f'Вогнутый прямой угол существует! {len(self.__field_boundary)}')
                    return False

        return is_angle

    def get_circle(self, local_points: list[Point]) -> bool:
        is_circle = False

        if self.is_point_on_circle(local_points[0]):
            return is_circle

        for i in range(3):
            if local_points[i].distance(local_points[i + 1]) > 50:
                return is_circle

        lines = [local_points[i] + local_points[j] for i in range(3) for j in range(i + 1, 4)]

        if 'k' in lines[0].line_equation.keys() and 'k' in lines[-1].line_equation.keys():
            equation1 = lines[0].line_equation
            equation2 = lines[-1].line_equation

            tangent = (equation2['k'] - equation1['k']) / (1 + equation2['k'] * equation1['k'])

            if 0.2 < math.fabs(math.atan(tangent)) < 1.0:
                is_circle = True

                intersection_points = [
                    lines[0].get_intersection(lines[1], median_perpendicular=True),
                    lines[1].get_intersection(lines[2], median_perpendicular=True),
                    lines[2].get_intersection(lines[0], median_perpendicular=True)
                ]

                center = Point(
                    (intersection_points[0].x + intersection_points[1].x + intersection_points[2].x) / 3,
                    (intersection_points[0].y + intersection_points[1].y + intersection_points[2].y) / 3
                )

                radii = [
                    center.distance(local_points[0]),
                    center.distance(local_points[1]),
                    center.distance(local_points[2]),
                ]

                radius = (radii[0] + radii[1] + radii[2]) / 3
                circle = Circle(center, radius, color=(255, 0, 0))

                if not circle.is_exist(self.__circles):
                    self.__circles.append(circle)
                else:
                    print('Окружность существует!')
                    is_circle = False

        return is_circle

    def get_rectangle(self):
        is_rectangle = False

        if not self.__straight_angles or len(self.__straight_angles) < 2:
            return is_rectangle

        groups = self.__groups_straight_angles

        for current in self.__straight_angles:
            if not current.is_convex:
                continue

            for neighbour in self.__straight_angles:
                if current == neighbour:
                    continue

                if not neighbour.is_convex:
                    continue

                rectangle_side = current.angle[1] + neighbour.angle[1]

                is_neighbours = False

                if rectangle_side.is_perpendicular(neighbour.angle[0]) or \
                        rectangle_side.is_perpendicular(neighbour.angle[2]):
                    is_neighbours = True

                ############
                # ДОПИЛИТЬ #
                ############
                if is_neighbours:

                    for line in self.__lines:
                        if not rectangle_side.merge_the_lines(line):
                            continue

                        if not (rectangle_side.start.distance(line.start) < 30 and
                                rectangle_side.end.distance(line.end) < 30):
                            continue

                        if current not in groups:
                            groups[current] = [neighbour]
                        elif neighbour not in groups[current]:
                            if len(groups[current]) < 2:
                                groups[current].append(neighbour)
                                # print(len(groups[current]))

                            if len(groups[current]) == 2:
                                other1 = groups[current][0].angle
                                other2 = groups[current][1].angle
                                is_find = False
                                point = None

                                if not is_find:
                                    if other1[0].is_perpendicular(other2[0]):
                                        point = other1[0].get_intersection(other2[0])
                                        if not point == current.angle[1]:
                                            is_find = True
                                if not is_find:
                                    if other1[0].is_perpendicular(other2[2]):
                                        point = other1[0].get_intersection(other2[2])
                                        if not point == current.angle[1]:
                                            is_find = True

                                if is_find:
                                    rect = Rectangle([
                                        current.angle[1],
                                        other1[1],
                                        point,
                                        other2[1]
                                    ],
                                        color=(0, 255, 0)
                                    )

                                    # rect = Rectangle([
                                    #     StraightAngle(line1=other1[1] + current.angle[1],
                                    #                   intersection=current.angle[1],
                                    #                   line2=other2[1] + current.angle[1]),
                                    #
                                    #     StraightAngle(line1=current.angle[1] + other1[1],
                                    #                   intersection=other1[1],
                                    #                   line2=point + other1[1]),
                                    #
                                    #     StraightAngle(line1=other1[1] + point,
                                    #                   intersection=point,
                                    #                   line2=other2[1] + point),
                                    #
                                    #     StraightAngle(line1=point + other2[1],
                                    #                   intersection=other2[1],
                                    #                   line2=current.angle[1] + other2[1])
                                    # ],
                                    #     color=(0, 255, 0)
                                    # )

                                    self.__rectangles.append(rect)

                                    for i in range(len(rect.larger_rectangle_points)):
                                        pts = rect.larger_rectangle_points
                                        self.__lines.append(pts[(i + 1) % 4] + pts[i])

        return is_rectangle

    def get_field_boundaries(self):
        if self.__field_boundary and len(self.__field_boundary) == 3:
            x = [item.angle[1].x for item in self.__field_boundary]
            y = [item.angle[1].y for item in self.__field_boundary]

            top_left_point = Point(min(x), max(y))
            top_right_point = Point(max(x), max(y))
            bottom_right_point = Point(max(x), min(y))
            bottom_left_point = Point(min(x), min(y))

            border = Border(
                Rectangle(
                    [
                        top_left_point,
                        top_right_point,
                        bottom_right_point,
                        bottom_left_point
                    ],
                    color=(255, 0, 247),
                    object_type='border'
                )
            )

            self.__rectangles.append(border)
