import numpy as np
from configs.settings import MIN_MARGIN, EPS, MAX_DISTANCE
import uuid
from typing import Optional


class Geometry:

    def __init__(self):
        self.id = uuid.uuid4()

    def __contains__(self, item):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


class Undefined(Geometry):

    def __init__(self, point):
        # TODO -- several points in "point"

        super().__init__()

        self.points = [point, ]

        self.complete = False

    def __contains__(self, point):

        distance = np.linalg.norm(np.array(self.points) - point, axis=1).min()

        if distance <= MIN_MARGIN:
            return True
        else:
            return False

    def append(self, point, condition=True):

        if condition:
            distance = np.linalg.norm(np.array(self.points) - point, axis=1).min()
            if distance > EPS:
                self.points.append(point)
        else:
            self.points.append(point)

    def _is_restangle(self) -> Optional['Restangle']:
        return None

    def _is_circle(self) -> Optional['Circle']:
        return None

    def _is_border(self) -> Optional['Restangle']:
        return None

    def detected(self):

        for method in [self._is_restangle, self._is_circle, self._is_border]:
            result = method()
            if result:
                return result


class Restangle:
    def __init__(self, points: list):
        super().__init__()

        # TODO -> в другое место
        data = np.array(points)

        # определим границы описывающего прямоугольника
        self.x_min, self.y_min = data[:, 0].min(), data[:, 1].min()
        self.x_max, self.y_max = data[:, 0].max(), data[:, 1].max()

        self.center = np.array(
            [[
                (self.x_min + self.x_max) / 2,
                (self.y_min + self.y_max) / 2,
            ]]
        )

        deltas = data - self.center
        angles = np.arctan2(deltas[:, 1], deltas[:, 0])
        angles = np.expand_dims(angles, axis=1)
        data = np.concatenate([data, angles], axis=1)
        data = data[data[:, 2].argsort()]
        data = data[:, :2]

        self.points = data

    def _contains(self, rectangle_points, point):
        point = np.array(point)
        count = rectangle_points.shape[0]
        sign = None

        for i in range(count):

            segment = rectangle_points[(i + 1) % count] - rectangle_points[i]
            to_point = point - rectangle_points[i]

            if sign is None:
                sign = np.dot(segment, to_point) > 0
            else:
                if sign != (np.dot(segment, to_point) > 0):
                    return False

        return True

    def __contains__(self, point):

        # TODO + 5*EPS
        rectangle_points = self.points
        return self._contains(rectangle_points, point)

    def __str__(self):
        return f"Rectangle: {self.points.tolist()}"


class Circle(Geometry):

    def __init__(self, center: list, radius: float):
        super().__init__()
        self.center = np.array(center)
        self.radius = radius

    def _contains(self, center, radius, point):
        point = np.array(point)
        if np.linalg.norm(center - point) < radius:
            return True
        return False

    def __contains__(self, point):
        point = np.array(point)
        return self._contains(self.center, self.radius + 5 * EPS, point)


class Border(Restangle):

    def __str__(self):
        return f"Border: {self.points.tolist()}"


if __name__ == '__main__':
    data = np.array([[-5, 5], [4, -3], [6, 2], [-5, -2.5]]) - [[0, 0]]
    list_data = data.tolist()
    rest = Restangle(list_data)
