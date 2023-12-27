import pymunk
from game.map import Map


class Scene:
    """
    Класс, который создает игровое поле
    """

    def __init__(self, space, path: str | None = None, map_object: Map | None = None):
        self.space = space

        if not path and not map_object:
            raise Exception('Путь к файлу с картой и объект карты не были переданы!')

        self.map = Map(path) if path else map_object

    def set_scene(self):
        """
        Установка карты.
        """

        count = len(self.map.border['coordinates'])

        for i in range(count):
            segment_shape_bottom = pymunk.Segment(
                self.space.static_body,
                self.map.border['coordinates'][i], self.map.border['coordinates'][(i + 1) % count],
                2
            )
            segment_shape_bottom.id = i
            segment_shape_bottom.body.position = 0, 0
            segment_shape_bottom.elasticity = 0.8
            segment_shape_bottom.friction = 1.0
            self.space.add(segment_shape_bottom)

        for circle in self.map.circles:
            circle_body = pymunk.Body(body_type=pymunk.Body.STATIC)
            circle_body.position = self.map.circles[circle]['center']
            circle_shape = pymunk.Circle(circle_body, self.map.circles[circle]['radius'])
            circle_shape.body = circle_body
            self.space.add(circle_shape, circle_body)

        for rectangle in self.map.rectangles:
            box_body = pymunk.Body(body_type=pymunk.Body.STATIC)
            box_body.position = 0, 0
            box_shape = pymunk.Poly(box_body, self.map.rectangles[rectangle]['coordinates'])
            box_shape.body = box_body
            self.space.add(box_shape, box_body)
