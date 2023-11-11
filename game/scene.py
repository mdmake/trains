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
