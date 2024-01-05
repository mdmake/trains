import math
import numpy as np

TOLERANCE = 3
ANGLE_TOLERANCE = 0.2
EPS = 1e-6


class Geometry:
    def __init__(
        self,
        color: tuple[int, int, int] = (0, 0, 0),
        object_type: str | None = None,
        **kwargs,
    ):
        self.__color = color
        self.__square = 0
        self.__object_type = object_type

    @property
    def object_type(self) -> str | None:
        return self.__object_type

    @property
    def color(self):
        return self.__color

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
        super().__init__(color=color, object_type="point")
        self.__x = x
        self.__y = y

    def almost_eq(self, other: "Point", tolerance=TOLERANCE):
        return self.distance(other) <= tolerance

    def __eq__(self, other: "Point") -> bool:
        """
        Проверка совпадения точек по расстоянию между ними с некоторой погрешностью.

        :param other: Точка (объект класса Point).
        :return: True, если расстояние между точками меньше некоторого значения, иначе - False.
        """

        return self.distance(other) < EPS

    def __hash__(self):
        return hash((self.__x, self.__y))

    def __add__(self, other: "Point") -> "Line":
        """
        Объединение двух точек (объекты класса Point) в прямую (объект класса Line). Например, line = point_1 + point_2.

        :param other: Точка (объект класса Point).
        :return: прямая (объект класса Line).
        """
        return Line(point0=self, point1=other)

    def __str__(self):
        return f"Точка с координатами ({self.__x}, {self.__y})"

    def __repr__(self):
        return f"Point({self.__x, self.__y})"

    def __contains__(self, points: list["Point"]) -> bool:
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

    def distance(self, other: "Point") -> float:
        """
        Получение расстояния между точками.

        :param other: Другая точка (объект класса Point), расстояние до которой нужно вычислить.
        :return: Расстояние между точками.
        """

        return math.sqrt((other.x - self.__x) ** 2 + (other.y - self.__y) ** 2)

    def vector(self, other: "Point") -> tuple[float, float]:
        """
        Получение вектора в виде кортежа двух координат в направлении от self к other.
        """
        return other.__x - self.__x, other.__y - self.__y


class Line(Geometry):
    """
    Класс "Прямая".
    """

    def __init__(
        self, point0: Point, point1: Point, color: tuple[int, int, int] = (255, 0, 0)
    ):
        # if point0 == point1:
        #     raise Exception('Начало и конец прямой не должны совпадать!')

        super().__init__(color=color, object_type="line")
        self.__point0 = point0
        self.__point1 = point1

    def __eq__(self, other: "Line"):
        return self.line == other.line

    def __str__(self):
        return f"Прямая, состоящая из точек ({self.point0.point}, {self.point1.point})"

    def __repr__(self):
        return f"Line(Point{self.__point0.point}, Point{self.point1.point})"

    def square(self):
        raise Exception("У прямой не может быть площади!")

    #
    # @property
    # def color(self):
    #     return self.__color

    @property
    def line(self):
        """
        Возвращает прямую в виде кортежа двух объектов класса Point.
        """
        return self.__point0, self.__point1

    @property
    def point0(self):
        """
        Возвращает начало прямой в виде объекта класса Point.
        """
        return self.__point0

    @property
    def point1(self):
        """
        Возвращает конец прямой в виде объекта класса Point.
        """
        return self.__point1

    @property
    def median_point(self) -> Point:
        """
        Возвращает кортеж координат середины отрезка (координата X, координата Y).
        """
        return Point(
            (self.__point0.x + self.point1.x) / 2, (self.point0.y + self.point1.y) / 2
        )

    def intersection(self, other: "Line") -> Point | None:
        """
        Вычисление точки пересечения двух прямых.

        :param other: Вторая прямая.
        :return: Point(x, y), если есть пересечения, иначе - None.
        """

        xdiff = (self.__point0.x - self.__point1.x, other.__point0.x - other.__point1.x)
        ydiff = (self.__point0.y - self.__point1.y, other.__point0.y - other.__point1.y)

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        div = det(xdiff, ydiff)

        if div == 0:
            return

        d = (
            det(self.__point0.point, self.__point1.point),
            det(other.__point0.point, other.__point1.point),
        )
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div

        return Point(x, y)

    def angle_between_lines(self, other: "Line"):
        """
        Вычисление угла между двумя прямыми.

        :param other: Вторая прямая.
        :return: Угол в радианах.
        """

        alpha = math.atan2(
            self.__point1.y - self.__point0.y, self.__point1.x - self.__point0.x
        )
        alpha = 2 * math.pi + alpha if alpha < 0 else alpha

        beta = math.atan2(
            other.__point1.y - other.__point0.y, other.__point1.x - other.__point0.x
        )
        beta = 2 * math.pi + beta if beta < 0 else beta

        result = alpha - beta if alpha > beta else beta - alpha

        return result - math.pi if result - math.pi > ANGLE_TOLERANCE else result

    def distance(self, other: "Point" or "Line") -> float:
        """
        Вычисление расстояния от прямой до точки/прямой.

        :param other: Точка или Прямая.
        :return: Расстояние.
        """

        if type(other) == Point:
            point = other

        elif type(other) == Line:
            if self == other or self.intersection(other):
                return 0.0

            point = other.__point0
        else:
            raise TypeError(f"Неизвестный тип параметра other: {type(other)}")

        up = (
            (self.__point0.y - self.__point1.y) * point.x
            + (self.__point1.x - self.__point0.x) * point.y
            + (self.__point0.x * self.__point1.y - self.__point1.x * self.__point0.y)
        )
        down = math.sqrt(
            (self.__point1.x - self.__point0.x) ** 2
            + (self.__point1.y - self.__point0.y) ** 2
        )

        return math.fabs(up / down)

    def __a_point_on_the_segment(self, point: Point) -> bool:
        """
        Определение нахождения точки на отрезке.

        :param point: Точка.
        :return: True, если точка находится на отрезке, иначе - False.
        """

        if not self.angle_between_lines(self.__point0 + point) < ANGLE_TOLERANCE:
            return False

        if (
            not math.pi - ANGLE_TOLERANCE
            < (point + self.__point0).angle_between_lines(point + self.__point1)
            < math.pi + ANGLE_TOLERANCE
        ):
            return False

        return True

    def parallel(self, other: "Line") -> bool:
        return (
            math.pi - ANGLE_TOLERANCE
            <= self.angle_between_lines(other)
            <= math.pi + ANGLE_TOLERANCE
            or self.angle_between_lines(other) <= ANGLE_TOLERANCE
        )

    def perpendicular(self, other: "Line") -> bool:
        return (
            (math.pi / 2) - ANGLE_TOLERANCE
            <= self.angle_between_lines(other)
            <= (math.pi / 2) + ANGLE_TOLERANCE
        )

    def combine_lines(self, other: "Line") -> "Line" or None:
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

        if self.__a_point_on_the_segment(other.__point0):
            first_point_on_segment = True

        if self.__a_point_on_the_segment(other.__point1):
            second_point_on_segment = True

        if first_point_on_segment and second_point_on_segment:
            return self

        if first_point_on_segment:
            if other.__point1.distance(self.__point1) <= other.__point1.distance(
                self.__point0
            ):
                return self.__point0 + other.__point1
            return self.__point1 + other.__point1

        elif second_point_on_segment:
            if other.__point0.distance(self.__point1) <= other.__point0.distance(
                self.__point0
            ):
                return self.__point0 + other.__point0
            return self.__point1 + other.__point0

    def is_point_on_it(self, point: Point) -> bool:
        """
        Проверка нахождения точки на прямой с некоторой погрешностью.

        :param point: Точка.
        :return: True, если точка находится на прямой, иначе - False.
        """

        cross = (point.x - self.__point0.x) * (self.__point1.y - self.__point0.y) - (
            point.y - self.__point0.y
        ) * (self.__point1.x - self.__point0.x)

        return math.fabs(cross) < TOLERANCE


class StraightAngle(Geometry):
    """
    Класс "Прямой угол"
    """

    def __init__(
        self,
        point0: Point,
        vertex: Point,
        point1: Point,
        color: tuple[int, int, int] = (0, 255, 0),
    ):
        self.__point0 = point0
        self.__vertex = vertex
        self.__point1 = point1

        self.__sign = False

        super().__init__(color=color, object_type="angle")
        self.set_color(color)

    def __hash__(self):
        return hash(self)

    def __eq__(self, other: "StraightAngle"):
        return (
            self.__point0 == other.__point0
            and self.__vertex == other.__vertex
            and self.__point1 == other.__point1
        )

    def __str__(self):
        return f"Прямой угол, состоящий из точек ({self.point0.point}, {self.__vertex.point},{self.point1.point})"

    def __repr__(self):
        return f"StraightAngle(Point{self.__point0.point}, Point{self.__vertex.point}, Point{self.__point1.point})"

    def square(self):
        raise Exception("У прямого угла не может быть площади!")

    def set_color(self, value: tuple[int, int, int]):
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

        intersection = (self.__point0 + self.__point1).intersection(
            train_position + self.__vertex
        )

        if intersection.distance(train_position) > self.__vertex.distance(
            train_position
        ):
            # Угол прямоугольника
            self.__sign = True
        else:
            # Угол границы поля
            self.__sign = False


class Circle(Geometry):
    """
    Класс "Окружность"
    """

    def __init__(
        self, center: Point, radius: float, color: tuple[int, int, int] = (0, 0, 0)
    ):
        super().__init__(color=color, object_type="circle")

        self.__center = center
        self.__radius = radius
        self.__points_on_it = []

        self.set_color(color)

    def __str__(self):
        return f"Окружность с центром O{self.__center.point} и радиусом R = {self.__radius})"

    def __repr__(self):
        return f"Circle(Point{self.__center.point}, {self.__radius})"

    def __contains__(self, point: Point):
        """
        Проверка точки на нахождение ее в/на окружности.

        :param point: Рассматриваемая точка.
        :return: True, если точка лежит в/на окружности, иначе - False.
        """

        return self.__center.distance(point) < self.__radius + TOLERANCE

    def __hash__(self):
        return hash(self)

    def __eq__(self, other: "Circle"):
        """
        Проверка эквивалентности окружностей.

        :param other: Другая окружность, с которой сравнивается текущая.
        :return: True, если окружности эквивалентны, иначе - False.
        """

        return (
            self.__center.distance(other.center) < TOLERANCE
            and math.fabs(self.__radius - other.__radius) < TOLERANCE
        )

    def set_color(self, value: tuple[int, int, int]):
        """
        Установка цвета для окружности.

        :param value: Цвет в RGB палитре. Например, (255, 255, 255).
        :return: None.
        """

        self.center.set_color(value)

    @property
    def square(self):
        return math.pi * self.__radius**2

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

    def __init__(
        self, vertices: list[Point], color=(0, 0, 0), object_type: str = "rectangle"
    ):
        super().__init__(color=color, object_type=object_type)

        self.__vertices: list[Point] = vertices
        self.__larger_rectangle_vertices: list[Point] = []

        self.set_color(color=color)
        self.sorting_vertices()
        self.set_larger_rectangle(epsilon=10)

    def __str__(self):
        return (
            f"Прямоугольник с вершинами "
            f"A{self.__vertices[0].point}, "
            f"B{self.__vertices[1].point}, "
            f"C{self.__vertices[2].point}, "
            f"D{self.__vertices[3].point}"
        )

    def __repr__(self):
        return (
            f"Rectangle(["
            f"Point{self.__vertices[0].point}, "
            f"Point{self.__vertices[1].point}, "
            f"Point{self.__vertices[2].point}, "
            f"Point{self.__vertices[3].point}])"
        )

    def __contains__(self, point: Point):
        """
        Проверка точки точки на нахождение ее в/на прямоугольнике.

        :param point: Точка, которую необходимо проверить.
        :return: True, если точка лежит в/на прямоугольнике, иначе - False.
        """
        rectangle = self.__larger_rectangle_vertices
        sign = None

        for i in range(4):
            side_vector = np.array(
                [
                    rectangle[(i + 1) % 4].x - rectangle[i].x,
                    rectangle[(i + 1) % 4].y - rectangle[i].y,
                ]
            )

            to_point_vector = np.array(
                [point.x - rectangle[i].x, point.y - rectangle[i].y]
            )
            print(to_point_vector)
            if not sign:
                sign = np.dot(side_vector, to_point_vector) < 0
            else:
                if sign != (np.dot(side_vector, to_point_vector) < 0):
                    return False
        return True

    def __eq__(self, other: "Rectangle"):
        return self == other

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
            sum(vertex.y for vertex in self.__vertices) / 4,
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
            self.__vertices[(i + 1) % 4] + self.__vertices[i]
            for i in range(len(self.__vertices))
        ]

    @property
    def square(self) -> float:
        """
        Вычисление площади прямоугольника.
        """
        return self.__vertices[0].distance(self.__vertices[1]) * self.__vertices[
            1
        ].distance(self.__vertices[2])

    def set_color(self, color) -> None:
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
            artan0 = math.atan2(
                self.__vertices[i].y - center_point.y,
                self.__vertices[i].x - center_point.x,
            )

            artan1 = math.atan2(
                self.__vertices[(i + 1) % 4].y - center_point.y,
                self.__vertices[(i + 1) % 4].x - center_point.x,
            )

            if artan0 < artan1:
                self.__vertices[i], self.__vertices[(i + 1) % 4] = (
                    self.__vertices[(i + 1) % 4],
                    self.__vertices[i],
                )

    def set_larger_rectangle(self, epsilon: float = 0.5):
        """
        Вычисление координат прямоугольника, большего, чем этот на величину epsilon.

        :param epsilon: Величина, на которую новый прямоугольник будет больше этого.
        """
        center_point = self.center

        if self.__larger_rectangle_vertices:
            for vertex in self.__vertices:
                dx = epsilon * math.cos(
                    math.atan2(vertex.y - center_point.y, vertex.x - center_point.x)
                )
                dy = epsilon * math.sin(
                    math.atan2(vertex.y - center_point.y, vertex.x - center_point.x)
                )

                self.__larger_rectangle_vertices.append(
                    Point(vertex.x + dx, vertex.y + dy)
                )


class Border(Rectangle):
    """
    Класс "Граница".
    """

    def __init__(
        self, vertices: list[Point], color: tuple[int, int, int] = (255, 0, 247)
    ):
        super().__init__(vertices=vertices, color=color, object_type="border")

    def __str__(self):
        return (
            f"Граница поля с вершинами "
            f"A{self.__vertices[0].point}, "
            f"B{self.__vertices[1].point}, "
            f"C{self.__vertices[2].point}, "
            f"D{self.__vertices[3].point}"
        )

    def __repr__(self):
        return (
            f"Border(["
            f"Point{self.__vertices[0].point}, "
            f"Point{self.__vertices[1].point}, "
            f"Point{self.__vertices[2].point}, "
            f"Point{self.__vertices[3].point}])"
        )

    def __contains__(self, point):
        for vertex in self.vertices:
            if (
                math.fabs(point.x - vertex.x) < TOLERANCE
                or math.fabs(point.y - vertex.y) < TOLERANCE
            ):
                return True
        return False


class Figures:
    """
    Класс "Фигуры"
    """

    def __init__(self):
        self.__points: list[Point] = []
        self.__lines: list[Line] = []
        self.__straight_angles: list[StraightAngle] = []
        self.__circles: list[Circle] = []
        self.__rectangles: list[Rectangle] = []
        self.__border: Border | None = None

        self.__field_boundary: list[StraightAngle] = []
        self.__groups_straight_angles: dict[StraightAngle, list[StraightAngle]] = dict()

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
        # if local_points in self:
        #     return False

        return self.get_line(local_points)
        # return self.get_angle(local_points, train_position) or \
        #        self.get_rectangle() or \
        #        self.get_line(local_points) or \
        #        self.get_circle(local_points)

    def is_point_on_the_border(self, point: Point) -> bool:
        if self.__border:
            for i in range(len(self.__field_boundary)):
                if point in self.__border:
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

                    buffer = current_line.combine_lines(other=next_line)

                    if buffer:
                        self.__lines[j] = buffer

                        if i > len(self.__lines) - 1:
                            return

                        self.__lines.pop(i)
                        continue
                    else:
                        j += 1

                i += 1
                j = 0

    def checking_for_overlapping_lines(self, line):
        merger = False
        index = 0

        while index < len(self.__lines):
            new_line = self.__lines[index].combine_lines(line)

            if new_line:
                self.__lines[index] = new_line
                line = new_line
                merger = True

            index += 1

        return merger

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

            new_line = other.combine_lines(main)
            # print(new_line)ee

            if new_line:
                # if not self.__lines or not self.checking_for_overlapping_lines(new_line):
                self.__lines.append(new_line)

                self.check()

            # if not self.__lines:
            #     self.__lines.append(new_line)
            # elif new_line:
            #     self.checking_for_overlapping_lines(new_line)

        return is_line

    def get_angle(self, local_points: list[Point], train_position: Point) -> bool:
        is_angle = False

        if local_points[0].is_exist(
            [local_points[1], local_points[2], local_points[3]]
        ):
            return is_angle

        distances = [
            local_points[i].distance(local_points[i + 1])
            for i in range(len(local_points) - 1)
        ]

        for i in range(len(distances)):
            if distances[i] > 50:
                return is_angle

        main_line = local_points[1] + local_points[0]

        other_line = local_points[2] + local_points[3]

        if (
            "k" in main_line.line_equation.keys()
            and "k" in other_line.line_equation.keys()
        ):
            equation1 = main_line.line_equation
            equation2 = other_line.line_equation

            tangent = (equation2["k"] - equation1["k"]) / (
                1 + equation2["k"] * equation1["k"]
            )

            if 1.5 < math.fabs(math.atan(tangent)) < 1.6:
                is_angle = True

        elif (
            "x" in main_line.line_equation.keys()
            and "y" in other_line.line_equation.keys()
        ):
            is_angle = True

        elif (
            "y" in main_line.line_equation.keys()
            and "x" in other_line.line_equation.keys()
        ):
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
                    print(f"Выпуклый прямой угол!")
                else:
                    print(f"Выпуклый прямой угол существует!")
                    return False
            else:
                if not self.__border and not straight_angle.is_exist(
                    self.__field_boundary
                ):
                    print(f"Вогнутый прямой угол!")
                    self.__field_boundary.append(straight_angle)
                    self.get_field_boundaries()
                else:
                    print(
                        f"Вогнутый прямой угол существует! {len(self.__field_boundary)}"
                    )
                    return False

        return is_angle

    def get_circle(self, local_points: list[Point]) -> bool:
        is_circle = False

        if self.is_point_on_circle(local_points[0]):
            return is_circle

        for i in range(3):
            if local_points[i].distance(local_points[i + 1]) > 50:
                return is_circle

        lines = [
            local_points[i] + local_points[j] for i in range(3) for j in range(i + 1, 4)
        ]

        if (
            "k" in lines[0].line_equation.keys()
            and "k" in lines[-1].line_equation.keys()
        ):
            equation1 = lines[0].line_equation
            equation2 = lines[-1].line_equation

            tangent = (equation2["k"] - equation1["k"]) / (
                1 + equation2["k"] * equation1["k"]
            )

            if 0.2 < math.fabs(math.atan(tangent)) < 1.0:
                is_circle = True

                intersection_points = [
                    lines[0].get_intersection(lines[1], median_perpendicular=True),
                    lines[1].get_intersection(lines[2], median_perpendicular=True),
                    lines[2].get_intersection(lines[0], median_perpendicular=True),
                ]

                center = Point(
                    (
                        intersection_points[0].x
                        + intersection_points[1].x
                        + intersection_points[2].x
                    )
                    / 3,
                    (
                        intersection_points[0].y
                        + intersection_points[1].y
                        + intersection_points[2].y
                    )
                    / 3,
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
                    print("Окружность существует!")
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

                if rectangle_side.is_perpendicular(
                    neighbour.angle[0]
                ) or rectangle_side.is_perpendicular(neighbour.angle[2]):
                    is_neighbours = True

                ############
                # ДОПИЛИТЬ #
                ############
                if is_neighbours:
                    for line in self.__lines:
                        if not rectangle_side.merge_the_lines(line):
                            continue

                        if not (
                            rectangle_side.start.distance(line.start) < 30
                            and rectangle_side.end.distance(line.end) < 30
                        ):
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
                                    rect = Rectangle(
                                        [current.angle[1], other1[1], point, other2[1]],
                                        color=(0, 255, 0),
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
                        bottom_left_point,
                    ],
                    color=(255, 0, 247),
                    object_type="border",
                )
            )

            self.__rectangles.append(border)
