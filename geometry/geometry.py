import math
from typing import Optional
from game.enumerators import ObjectType, Color

TOLERANCE = 3
ANGLE_TOLERANCE = 0.2


class Geometry:
    def __init__(self, color=Color.BLACK, object_type: Optional[ObjectType] = None):
        self.__color = color
        self.__square = 0
        self.__object_type = object_type

    @property
    def object_type(self) -> str | None:
        return self.__object_type

    @property
    def color(self):
        return self.__color.value

    def set_color(self, color: Color):
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

    def __init__(self, x: float, y: float, color=Color.BLUE):
        super().__init__(color=color, object_type=ObjectType.POINT)
        self.__x = x
        self.__y = y

    def almost_eq(self, other: 'Point', tolerance=TOLERANCE):
        return self.distance(other) <= tolerance

    def __eq__(self, other: 'Point') -> bool:
        """
        Проверка совпадения точек по расстоянию между ними с некоторой погрешностью.

        :param other: Точка (объект класса Point).
        :return: True, если расстояние между точками меньше некоторого значения, иначе - False.
        """

        return self.distance(other) == 0

    def __hash__(self):
        return hash((self.__x, self.__y))

    def __add__(self, other: Optional['Point']) -> 'Line':
        """
        Объединение двух точек (объекты класса Point) в прямую (объект класса Line). Например, line = point_1 + point_2.

        :param other: Точка (объект класса Point).
        :return: прямая (объект класса Line).
        """
        if other.object_type != ObjectType.POINT:
            raise TypeError
        return Line(point0=self, point1=other)

    def __str__(self):
        return f'Точка с координатами ({self.__x}, {self.__y})'

    def __repr__(self):
        return f'Point({self.__x, self.__y})'

    def __contains__(self, points: list['Point']) -> bool:
        """
        Проверка наличия точки в списке точек.

        :param points: Список объектов класса Point.
        :return: True, если точка есть в списке points, иначе - False.
        """

        for other in points:
            if self == other:
                return True

        return False

    def square(self):
        raise NotImplementedError

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

    def distance(self, other: 'Point') -> Optional[float]:
        """
        Получение расстояния между точками.

        :param other: Другая точка (объект класса Point), расстояние до которой нужно вычислить.
        :return: Расстояние между точками.
        """
        return math.sqrt((other.__x - self.__x) ** 2 + (other.__y - self.__y) ** 2)

    def calculate_point_coordinates(self, other: 'Point', length: float, flag=False) -> Optional['Point']:
        """
        Вычисление точки, в направлении вектора заданной длинны.

        :param other: Вторая точка.
        :param length: Смещение изначальной точки.
        :param flag: True, если смещаем self в направлении к other, иначе - False.
        :return: Промежуточная точка.
        """
        if flag:
            dx = other.__x - self.__x
            dy = other.__y - self.__y
        else:
            dx = self.__x - other.__x
            dy = self.__y - other.__y

        return Point(self.__x + length * math.cos(math.atan2(dy, dx)),
                     self.__y + length * math.sin(math.atan2(dy, dx)))


class Line(Geometry):
    """
    Класс "Прямая".
    """

    def __init__(self, point0: Point, point1: Point, color=Color.PURPLE):
        # if __begin_at == __final_at:
        #     raise Exception('Начало и конец прямой не должны совпадать!')

        super().__init__(color=color, object_type=ObjectType.LINE)
        self.__point0 = point0
        self.__point1 = point1

    def __eq__(self, other: 'Line'):
        return self.line == other.line

    def __str__(self):
        return f'Прямая, состоящая из точек ({self.point0.point}, {self.point1.point})'

    def __repr__(self):
        return f'Line(Point{self.__point0.point}, Point{self.point1.point})'

    def square(self):
        raise Exception('У прямой не может быть площади!')

    @property
    def line(self) -> tuple[Point, Point]:
        """
        Возвращает прямую в виде кортежа двух объектов класса Point.
        """
        return self.__point0, self.__point1

    @property
    def point0(self) -> Point:
        """
        Возвращает начало прямой в виде объекта класса Point.
        """
        return self.__point0

    @property
    def point1(self) -> Point:
        """
        Возвращает конец прямой в виде объекта класса Point.
        """
        return self.__point1

    @property
    def median_point(self) -> Point:
        """
        Возвращает кортеж координат середины отрезка (координата X, координата Y).
        """
        return Point((self.__point0.x + self.point1.x) / 2, (self.point0.y + self.point1.y) / 2)

    def intersection(self, other: 'Line') -> Optional[Point]:
        """
        Вычисление точки пересечения двух прямых.

        :param other: Вторая прямая.
        :return: Point(x, y), если есть пересечения, иначе - None.
        """
        if other.object_type != ObjectType.LINE:
            raise TypeError

        xdiff = (self.__point0.x - self.__point1.x, other.__point0.x - other.__point1.x)
        ydiff = (self.__point0.y - self.__point1.y, other.__point0.y - other.__point1.y)

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        div = det(xdiff, ydiff)

        if div == 0:
            return

        d = (det(self.__point0.point, self.__point1.point), det(other.__point0.point, other.__point1.point))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div

        point = Point(x, y)

        if self.is_point_on_the_segment(point):
            return point

    def projection(self, point: Optional[Point]) -> Optional[Point]:
        """
        Вычисляется проекция точки на прямую.

        :param point: Точка, которую необходимо спроецировать.
        :return: Проекция точки.
        """
        if point.object_type != ObjectType.POINT:
            raise TypeError

        line_v = Point(self.point1.x - self.point0.x, self.point1.y - self.point0.y)
        point_v = Point(point.x - self.point0.x, point.y - self.point0.y)
        factor = (point_v.x * line_v.x + point_v.y * line_v.y) / (line_v.x ** 2 + line_v.y ** 2)

        return Point(self.point0.x + factor * line_v.x, self.point0.y + factor * line_v.y)

    def angle_between_lines(self, other: Optional['Line']):
        """
        Вычисление угла между двумя прямыми.

        :param other: Вторая прямая.
        :return: Угол в радианах.
        """
        if other.object_type != ObjectType.LINE:
            raise TypeError

        alpha = math.atan2(self.__point1.y - self.__point0.y, self.__point1.x - self.__point0.x)
        alpha = 2 * math.pi + alpha if alpha < 0 else alpha

        beta = math.atan2(other.__point1.y - other.__point0.y, other.__point1.x - other.__point0.x)
        beta = 2 * math.pi + beta if beta < 0 else beta

        result = alpha - beta if alpha > beta else beta - alpha

        return result - math.pi if result - math.pi > ANGLE_TOLERANCE else result

    def distance(self, other: Optional['Point' or 'Line']) -> float:
        """
        Вычисление расстояния от прямой до точки/прямой.

        :param other: Точка или Прямая.
        :return: Расстояние.
        """
        if other.object_type == ObjectType.POINT:
            point = other

        elif other.object_type == ObjectType.LINE:
            if self == other or self.intersection(other):
                return .0

            point = other.__point0
        else:
            raise TypeError

        up = (self.__point0.y - self.__point1.y) * point.x + (self.__point1.x - self.__point0.x) * point.y + \
             (self.__point0.x * self.__point1.y - self.__point1.x * self.__point0.y)
        down = math.sqrt((self.__point1.x - self.__point0.x) ** 2 + (self.__point1.y - self.__point0.y) ** 2)

        return math.fabs(up / down)

    def is_point_on_the_segment(self, point: Point) -> bool:
        """
        Определение нахождения точки на отрезке.

        :param point: Точка.
        :return: True, если точка находится на отрезке, иначе - False.
        """
        angle = self.angle_between_lines(self.__point0 + point)

        if not angle < ANGLE_TOLERANCE:
            return False

        angle = (point + self.__point0).angle_between_lines(point + self.__point1)

        if not math.pi - ANGLE_TOLERANCE < angle < math.pi + ANGLE_TOLERANCE:
            return False

        return True

    def parallel(self, other: 'Line') -> bool:
        return math.pi - ANGLE_TOLERANCE <= self.angle_between_lines(other) <= math.pi + ANGLE_TOLERANCE or\
               self.angle_between_lines(other) <= ANGLE_TOLERANCE

    # Не используется
    # def perpendicular(self, other: 'Line') -> bool:
    #     return (math.pi / 2) - ANGLE_TOLERANCE <= self.angle_between_lines(other) <= (math.pi / 2) + ANGLE_TOLERANCE

    def combine_lines(self, other: 'Line') -> 'Line' or None:
        """
        Объединение двух отрезков в один.

        :param other: Второй отрезок.
        :return: Новый отрезок, если отрезки можно объединить в один, иначе - False.
        """
        if not self.parallel(other):
            return

        if not self.distance(other) <= TOLERANCE:
            return

        first_point_on_segment = False
        second_point_on_segment = False

        if self.is_point_on_the_segment(other.__point0):
            first_point_on_segment = True

        if self.is_point_on_the_segment(other.__point1):
            second_point_on_segment = True

        if first_point_on_segment and second_point_on_segment:
            return self

        if first_point_on_segment:
            if other.__point1.distance(self.__point1) <= other.__point1.distance(self.__point0):
                return self.__point0 + other.__point1
            return self.__point1 + other.__point1

        elif second_point_on_segment:
            if other.__point0.distance(self.__point1) <= other.__point0.distance(self.__point0):
                return self.__point0 + other.__point0
            return self.__point1 + other.__point0

    def side_of_point(self, point):
        """
        Определение расположения точки относительно прямой.

        :param point: Точка.
        :return: Если result > 0, то точка находится справа от прямой,
                 Если result < 0, то точка находится слева от прямой,
                 Если result = 0, то точка находится на прямой.
        """
        return (point.x - self.__point0.x) * (self.__point1.y - self.__point0.y) - \
               (point.y - self.__point0.y) * (self.__point1.x - self.__point0.x)


class StraightAngle(Geometry):
    """
    Класс "Прямой угол"
    """

    def __init__(self, point0: Point, vertex: Point, point1: Point, color=Color.GREEN):
        self.__point0 = point0
        self.__vertex = vertex
        self.__point1 = point1

        self.__sign = False

        super().__init__(color=color, object_type=ObjectType.ANGLE)
        self.set_color(color)

    def __hash__(self):
        return hash(self)

    def __eq__(self, other: 'StraightAngle'):
        return self.__point0 == other.__point0 and \
               self.__vertex == other.__vertex and \
               self.__point1 == other.__point1

    def __str__(self):
        return f'Прямой угол, состоящий из точек ({self.point0.point}, {self.__vertex.point},{self.point1.point})'

    def __repr__(self):
        return f'StraightAngle(Point{self.__point0.point}, Point{self.__vertex.point}, Point{self.__point1.point})'

    def square(self):
        raise Exception('У прямого угла не может быть площади!')

    def set_color(self, value: Color):
        """
        Установка цвета.

        :param value: Цвет в RGB палитре.
        :return:
        """
        self.__point0.set_color(value)
        self.__point1.set_color(value)
        self.__vertex.set_color(value)

    @property
    def point0(self) -> Point:
        """
        Получение первой точки угла.
        """
        return self.__point0

    @property
    def vertex(self) -> Point:
        """
        Получение вершины угла.
        """
        return self.__vertex

    @property
    def point1(self):
        """
        Получение второй точки угла.
        """
        return self.__point1

    @property
    def sign(self) -> bool:
        """
        Получение признака принадлежности угла прямоугольнику.
        """
        return self.__sign

    def set_sign(self, train_position: Point):
        """
        Установка признака. True, если это угол, принадлежащий прямоугольнику, иначе - False.

        :param train_position: Координаты поезда.
        :return: None.
        """

        intersection = (self.__point0 + self.__point1).intersection(train_position + self.__vertex)

        if intersection.distance(train_position) > self.__vertex.distance(train_position):
            # Угол прямоугольника
            self.__sign = True
        else:
            # Угол границы поля
            self.__sign = False


class Circle(Geometry):
    """
    Класс "Окружность"
    """

    def __init__(self, center: Point, radius: float, color=Color.BLACK):
        super().__init__(color=color, object_type=ObjectType.CIRCLE)

        self.__center = center
        self.__radius = radius
        self.__points_on_it = []

        self.set_color(color)

    def __str__(self):
        return f'Окружность с центром O{self.__center.point} и радиусом R = {self.__radius})'

    def __repr__(self):
        return f'Circle(Point{self.__center.point}, {self.__radius})'

    def __contains__(self, point: Point):
        """
        Проверка точки на нахождение ее в/на окружности.

        :param point: Рассматриваемая точка.
        :return: True, если точка лежит в/на окружности, иначе - False.
        """

        return self.__center.distance(point) < self.__radius + TOLERANCE

    def __hash__(self):
        return hash((self.__center, self.__radius))

    def __eq__(self, other: 'Circle'):
        """
        Проверка эквивалентности окружностей.

        :param other: Другая окружность, с которой сравнивается текущая.
        :return: True, если окружности эквивалентны, иначе - False.
        """

        return self.__center.distance(other.center) < TOLERANCE and \
            math.fabs(self.__radius - other.__radius) < TOLERANCE

    def intersection(self, other: 'Line' or 'Circle') -> tuple[Point, Point] | Point | None:
        """
        Высчитываются точки пересечения окружности и окружности/прямой.

        :param other: Окружность/прямая.
        :return: Две/одна точки пересечения - окружности (прямая и окружность) пересекаются/касаются.
                 None - окружности совпадают
                 или одна окружность находится в другой,
                 или окружности не пересекаются/касаются,
                 или прямая не пересекает окружность.
        """

        if other.object_type == ObjectType.LINE:
            point = other.projection(self.__center)

            if self.__center.distance(point) > self.__radius:
                return

            circle = Circle(point, math.sqrt(self.__radius ** 2 - self.__center.distance(point) ** 2))

            if self.__center.distance(circle.__center) == 0:
                points = self.center.calculate_point_coordinates(other.point0, self.__radius, flag=True),\
                         self.center.calculate_point_coordinates(other.point1, self.__radius, flag=True)

                if other.is_point_on_the_segment(points[0]) and other.is_point_on_the_segment(points[1]):
                    return points
                elif other.is_point_on_the_segment(points[0]):
                    return points[0]
                elif other.is_point_on_the_segment(points[1]):
                    return points[1]
                else:
                    return
        elif other.object_type == ObjectType.CIRCLE:
            circle = other

            if self.__center.distance(circle.__center) == 0:
                return
        else:
            raise TypeError

        if self.__center.distance(circle.__center) > self.__radius + circle.__radius:
            return

        a_side = self.__radius
        b_side = circle.__radius
        c_side = self.__center.distance(circle.__center)

        dx = circle.__center.x - self.__center.x
        dy = circle.__center.y - self.__center.y

        square_a = a_side ** 2
        square_b = b_side ** 2
        square_c = c_side ** 2

        cos = (square_a - square_b + square_c) / (a_side * c_side * 2)

        angle_of_rotation = math.acos(cos)
        angle_correction = math.atan2(dy, dx)

        x1 = self.__center.x + math.cos(angle_correction - angle_of_rotation) * a_side
        y1 = self.__center.y + math.sin(angle_correction - angle_of_rotation) * a_side

        result_point_1 = Point(x1, y1)

        if self.__center.distance(circle.__center) == self.__radius + circle.__radius:
            if other.object_type == ObjectType.LINE:
                if other.is_point_on_the_segment(result_point_1):
                    return result_point_1
            else:
                return result_point_1

        x2 = self.__center.x + math.cos(angle_correction + angle_of_rotation) * a_side
        y2 = self.__center.y + math.sin(angle_correction + angle_of_rotation) * a_side

        result_point_2 = Point(x2, y2)

        if other.object_type == ObjectType.LINE:
            if other.is_point_on_the_segment(result_point_1) and other.is_point_on_the_segment(result_point_2):
                return result_point_1, result_point_2
            elif other.is_point_on_the_segment(result_point_1):
                return result_point_1
            elif other.is_point_on_the_segment(result_point_2):
                return result_point_2
        else:
            return result_point_1, result_point_2

    def set_color(self, value: Color):
        """
        Установка цвета для окружности.

        :param value: Цвет в RGB палитре. Например, (255, 255, 255).
        :return: None.
        """

        self.center.set_color(value)

    @property
    def square(self):
        return math.pi * self.__radius ** 2

    @property
    def points_on_it(self) -> list[Point]:
        """
        Получение точек, принадлежащих окружности.
        """

        return self.__points_on_it

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


class Rectangle(Geometry):
    """
    Класс "Прямоугольник".
    """

    def __init__(self, vertices: list[Point], color=Color.BLACK, object_type=ObjectType.RECTANGLE):
        super().__init__(color=color, object_type=object_type)

        self.__vertices: list[Point] = vertices
        self.__larger_rectangle_vertices: list[Point] = []

        self.set_color(color=color)
        self.sorting_vertices()
        self.set_larger_rectangle(epsilon=10)

    def __str__(self):
        return f'Прямоугольник с вершинами ' \
               f'A{self.__vertices[0].point}, ' \
               f'B{self.__vertices[1].point}, ' \
               f'C{self.__vertices[2].point}, ' \
               f'D{self.__vertices[3].point}'

    def __repr__(self):
        return f'Rectangle([' \
               f'Point{self.__vertices[0].point}, ' \
               f'Point{self.__vertices[1].point}, ' \
               f'Point{self.__vertices[2].point}, ' \
               f'Point{self.__vertices[3].point}])'

    def __contains__(self, point: Point):
        """
        Проверка точки точки на нахождение ее в/на прямоугольнике.

        :param point: Точка, которую необходимо проверить.
        :return: True, если точка лежит в/на прямоугольнике, иначе - False.
        """
        sides = self.sides

        for i in range(4):
            sign = (point.x - sides[i].point0.x) * (sides[i].point1.y - sides[i].point0.y) - \
                   (point.y - sides[i].point0.y) * (sides[i].point1.x - sides[i].point0.x)
            if sign >= 0:
                return False
        return True

    def __eq__(self, other: 'Rectangle'):
        return self.__vertices == other.__vertices

    @property
    def larger_rectangle(self):
        return self.__larger_rectangle_vertices

    @property
    def center(self) -> Point:
        """
        Получение центра прямоугольника.
        """
        return Point(
            sum(vertex.x for vertex in self.__vertices) / 4,
            sum(vertex.y for vertex in self.__vertices) / 4
        )

    @property
    def vertices(self) -> list[Point]:
        """
        Получение списка из 4x точек, составляющих прямоугольник.
        """
        return self.__vertices

    @property
    def sides(self) -> list[Line]:
        """
        Получение сторон прямоугольника.
        """
        return [
            self.__vertices[i] + self.__vertices[(i + 1) % 4]
            for i in range(len(self.__vertices))
        ]

    @property
    def square(self) -> float:
        """
        Вычисление площади прямоугольника.
        """
        return self.__vertices[0].distance(self.__vertices[1]) * self.__vertices[1].distance(self.__vertices[2])

    def set_color(self, color: Color) -> None:
        """
        Установка цвета для прямоугольника.

        :param color: Цвет, представленный в RGB палитре. Например, (255, 255, 255).
        """
        for vertex in self.__vertices:
            vertex.set_color(color)

    def sorting_vertices(self):
        """
        Сортировка вершин прямоугольника. В итоге, вершины идут против часовой стрелки относительно центра
        прямоугольника.

        :return: None.
        """
        center_point = self.center

        for i in range(len(self.__vertices)):
            for j in range(len(self.__vertices)):

                artan0 = math.atan2(
                    self.__vertices[i].y - center_point.y,
                    self.__vertices[i].x - center_point.x
                )

                artan1 = math.atan2(
                    self.__vertices[j].y - center_point.y,
                    self.__vertices[j].x - center_point.x
                )

                if artan0 < artan1:
                    self.__vertices[i], self.__vertices[j] = self.__vertices[j], self.__vertices[i]

    def set_larger_rectangle(self, epsilon: float = 0.5):
        """
        Вычисление координат прямоугольника, большего, чем этот на величину epsilon.

        :param epsilon: Величина, на которую новый прямоугольник будет больше этого.
        """
        center_point = self.center

        if self.__larger_rectangle_vertices:
            for vertex in self.__vertices:
                dx = epsilon * math.cos(math.atan2(vertex.y - center_point.y, vertex.x - center_point.x))
                dy = epsilon * math.sin(math.atan2(vertex.y - center_point.y, vertex.x - center_point.x))

                self.__larger_rectangle_vertices.append(Point(vertex.x + dx, vertex.y + dy))

    def intersection(self, other: 'Line' or 'Circle' or 'Rectangle'):
        """
        Вычисление пересечения прямоугольника с прямой/окружностью/прямоугольником.

        :param other: Объект типа Line/Circle/Rectangle.
        :return: Точка(-и) пересечения, если пересечение есть, иначе - None.
        """
        if other.object_type == ObjectType.LINE:
            for side in self.sides:
                point = side.intersection(other)

                if not point:
                    continue

                if side.is_point_on_the_segment(point) and other.is_point_on_the_segment(point):
                    return point
        elif other.object_type == ObjectType.CIRCLE:
            for side in self.sides:
                points = other.intersection(side)

                if not points:
                    continue

                if type(points) == tuple:
                    if side.is_point_on_the_segment(points[0]) and side.is_point_on_the_segment(points[1]):
                        return points
                    elif side.is_point_on_the_segment(points[0]):
                        return points[0]
                    elif side.is_point_on_the_segment(points[1]):
                        return points[1]
                else:
                    if side.is_point_on_the_segment(points):
                        return points

        elif other.object_type == ObjectType.RECTANGLE:
            for self_side in self.sides:
                for other_side in other.sides:
                    point = self_side.intersection(other_side)

                    if not point:
                        continue

                    if self_side.is_point_on_the_segment(point) and other_side.is_point_on_the_segment(point):
                        return point
        else:
            raise TypeError


class Border(Rectangle):
    """
    Класс "Граница".
    """

    def __init__(self, vertices: list[Point], color=Color.PURPLE):
        super().__init__(vertices=vertices, color=color, object_type=ObjectType.BORDER)

    def __str__(self):
        return f'Граница поля с вершинами ' \
               f'A{self.__vertices[0].point}, ' \
               f'B{self.__vertices[1].point}, ' \
               f'C{self.__vertices[2].point}, ' \
               f'D{self.__vertices[3].point}'

    def __repr__(self):
        return f'Border([' \
               f'Point{self.__vertices[0].point}, ' \
               f'Point{self.__vertices[1].point}, ' \
               f'Point{self.__vertices[2].point}, ' \
               f'Point{self.__vertices[3].point}])'

    def __contains__(self, point):
        for vertex in self.vertices:
            if math.fabs(point.x - vertex.x) < TOLERANCE or math.fabs(point.y - vertex.y) < TOLERANCE:
                return True
        return False
