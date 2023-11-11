import pymunk
from math import radians
import yaml


class Scene:
    """
    Класс, который создает игровое поле
    """

    def __init__(self, filename, space):
        self.space = space
        with open(filename, 'r') as f:
            data = yaml.safe_load(f)
            self.border = data['border']
            self.objects = data['objects']
            self.description = data['description']
            self._complete = self.description['complete']

    def set_scene(self):
        count = len(self.border['coordinates'])
        for i in range(count):
            segment_shape_bottom = pymunk.Segment(
                self.space.static_body,
                self.border['coordinates'][i], self.border['coordinates'][(i + 1) % count],
                2
            )
            segment_shape_bottom.id = i
            segment_shape_bottom.body.position = 0, 0
            segment_shape_bottom.elasticity = 0.8
            segment_shape_bottom.friction = 1.0
            self.space.add(segment_shape_bottom)

        for k, object in self.objects.items():
            if object['type'] == "circle":
                circle_body = pymunk.Body(body_type=pymunk.Body.STATIC)
                circle_body.position = object['center']
                circle_shape = pymunk.Circle(circle_body, object['radius'])
                circle_shape.body = circle_body
                self.space.add(circle_shape, circle_body)
            elif object['type'] == "rectangle":
                box_body = pymunk.Body(body_type=pymunk.Body.STATIC)
                box_body.position = 0, 0
                box_shape = pymunk.Poly(box_body, object['coordinates'])
                box_shape.body = box_body
                self.space.add(box_shape, box_body)
            else:
                error_message = f"Unknown type: {object['type']}"
                raise KeyError(error_message)

    def set_default_scene(self, *, space: pymunk.Space, width: int = 1280, height: int = 720, margin: int = 0):
        """
        Создать игровое поле по умолчанию. Расстановка препятствий сделана вручную для поля 1280х720

        :param space: pymunk.Space
        :param width: ширина игрового полы
        :param height: высота инрового поля
        :param margin: отступ препятствий от краев игрового поля
        """

        pass

        # низ
        segment_shape_bottom = pymunk.Segment(space.static_body, (0 + margin, 0 + margin),
                                              (width - margin * 2, 0 + margin),
                                              2)
        segment_shape_bottom.id = 1
        segment_shape_bottom.body.position = 0, 0
        segment_shape_bottom.elasticity = 0.8
        segment_shape_bottom.friction = 1.0
        space.add(segment_shape_bottom)

        # верх
        segment_shape_top = pymunk.Segment(space.static_body, (0 + margin, 0 - margin),
                                           (width - margin * 2, 0 - margin), 2)
        segment_shape_top.id = 2
        segment_shape_top.body.position = 0, height
        segment_shape_top.elasticity = 0.8
        segment_shape_top.friction = 1.0
        space.add(segment_shape_top)

        # left border
        segment_shape_left = pymunk.Segment(
            space.static_body,
            (0 + margin, 0 + margin),
            (0 + margin, height - margin),
            2
        )

        segment_shape_left.id = 3
        segment_shape_left.body.position = 0, 0
        segment_shape_left.elasticity = 0.8
        segment_shape_left.friction = 1.0
        space.add(segment_shape_left)

        # right border
        segment_shape_right = pymunk.Segment(
            space.static_body,
            (0 - margin * 2, 0 + margin),
            (0 - margin * 2, height - margin), 2
        )
        segment_shape_right.id = 4
        segment_shape_right.body.position = width, 0
        segment_shape_right.elasticity = 0.8
        segment_shape_right.friction = 1.0
        space.add(segment_shape_right)

        circle_body_1 = pymunk.Body(body_type=pymunk.Body.STATIC)
        circle_body_1.position = 300, 300
        circle_shape_1 = pymunk.Circle(circle_body_1, 50)
        circle_shape_1.body = circle_body_1
        space.add(circle_shape_1, circle_body_1)

        circle_body_2 = pymunk.Body(body_type=pymunk.Body.STATIC)
        circle_body_2.position = 500, 500
        circle_shape_2 = pymunk.Circle(circle_body_2, 70)
        circle_shape_2.body = circle_body_2
        space.add(circle_shape_2, circle_body_2)

        box_body_1 = pymunk.Body(body_type=pymunk.Body.STATIC)
        box_body_1.position = 1000, 400
        box_body_1.angle = radians(20)
        box_shape_1 = pymunk.Poly.create_box(box_body_1, (70, 200))
        box_shape_1.body = box_body_1
        space.add(box_shape_1, box_body_1)

        box_body_2 = pymunk.Body(body_type=pymunk.Body.STATIC)
        box_body_2.position = 800, 100
        box_shape_2 = pymunk.Poly.create_box(box_body_2, (300, 50))
        box_shape_2.body = box_body_2
        space.add(box_shape_2, box_body_2)
