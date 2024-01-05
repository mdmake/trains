from configs.settings import EPS
from game.map import Map
from game.mathfunction import distanse2D

CLUSTER_DISTANCE = 20


class Cluster:
    def __init__(self, points: list = None):
        self.points = points or []
        self.itr = None

    def __contains__(self, item: tuple[int | float, int | float]):
        # print('test'*20)
        for point in self:
            if distanse2D(item, point) < EPS:
                return True
        return False

    def belong(self, item: tuple[int | float, int | float]):
        for point in self:
            if distanse2D(item, point) < CLUSTER_DISTANCE:
                return True
        return False

    def is_same(self, other: "Cluster"):
        for point in self:
            for other_point in other:
                if distanse2D(other_point, point) < CLUSTER_DISTANCE:
                    return True
        return False

    def append_cluster(self, other):
        self.points = self.points + other.points

    def append(self, item):
        self.points.append(item)

    def __iter__(self):
        self.itr = iter(self.points)
        return self

    def __next__(self):
        return next(self.itr)


class Cartographer:
    def __init__(self, map: Map = None):
        self.map = map or Map()
        self.is_complete = self.map.complete

        self.border = None
        self.objects = []
        self.clusters = []

    def append(self, points: list):
        for point in points:
            for cluster in self.clusters:
                if cluster.belong(point):
                    cluster.append(point)
                    break
            else:
                self.clusters.append(
                    Cluster(
                        [
                            point,
                        ]
                    )
                )

    def update(self):
        clusters = [[item, True] for item in self.clusters]

        for i in range(len(clusters)):
            if clusters[i][1]:
                for j in range(i + 1, len(clusters)):
                    if clusters[i][0].is_same(clusters[j][0]):
                        clusters[j][0].append_cluster(clusters[i][0])
                        clusters[i][1] = False
                        break

        self.clusters = [item[0] for item in clusters if item[1]]

    def save(self):
        pass
