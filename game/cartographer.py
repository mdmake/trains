from game.map import Map
from game.mathfunction import distanse2D

CLUSTER_DISTANCE = 20


class Cluster:
    def __init__(self, points: list = None):
        self.points = []
        self.itr = None
        self.center = None
        self.radius = None
        self.updated = False

        if points:
            self.points = [
                points[0],
            ]
            self.radius = 0
            self.center = points[0]
            self.update_center_and_radius(self.points[1:])

    def update_center_and_radius(self, points):
        x_center, y_center = self.center
        radius = self.radius

        for x, y in points:
            x_center = (x_center * len(self.points) + x) / (len(self.points) + 1)
            y_center = (y_center * len(self.points) + y) / (len(self.points) + 1)

            radius = max(radius, distanse2D((x_center, y_center), (x, y)))

        self.center = (x_center, y_center)
        self.radius = radius

    def __contains__(self, item: tuple[int | float, int | float]):
        return item in self.points

    def belong(self, item: tuple[int | float, int | float]):
        for point in self.points:
            if distanse2D(item, point) < CLUSTER_DISTANCE:
                return True
        return False

    def is_same(self, other: "Cluster"):
        if self.radius + other.radius < distanse2D(self.center, other.center):
            return False

        for point in self:
            for other_point in other:
                if distanse2D(other_point, point) < CLUSTER_DISTANCE:
                    return True
        return False

    def append_clusters(self, others):
        for other in others:
            self.points += other.points

        x_center, y_center, radius = 0, 0, 0
        for x, y in self.points:
            x_center += x
            y_center += y

        self.center = (x_center / len(self.points), y_center / len(self.points))

        for x, y in self.points:
            distance = distanse2D((x, y), self.center)
            if radius < distance:
                radius = distance

        self.radius = radius

    def append(self, item):
        if item in self.points:
            return

        self.points.append(item)
        self.update_center_and_radius(
            [
                item,
            ]
        )
        self.updated = True

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
        for item in points:
            find_cluster = 0
            point = (round(item[0], 0), round(item[1], 0))
            for i, cluster in enumerate(self.clusters):
                if (
                    distanse2D(point, cluster.center)
                    < cluster.radius + CLUSTER_DISTANCE
                ):
                    if cluster.belong(point):
                        cluster.append(point)
                        find_cluster += 1

            if not find_cluster:
                self.clusters.append(
                    Cluster(
                        [
                            point,
                        ]
                    )
                )

            if find_cluster > 1:
                old_clusters = [c for c in self.clusters if c.updated is False]
                new_clusters = [c for c in self.clusters if c.updated is True]

                new_cluster = new_clusters[0]
                new_cluster.append_clusters(new_clusters[1:])
                self.clusters = old_clusters + [
                    new_cluster,
                ]

            for i in range(len(self.clusters)):
                self.clusters[i].updated = False

    def save(self):
        pass
