from game.map import Map

from geometry import Circle, Restangle, Border, Undefined


class Cartographer:

    def __init__(self, map: Map = None):
        self.map = map or Map()
        self.is_complete = self.map.complete

        self.border = None
        self.objects = []

        # TODO -- color
        for object in self.objects:
            if object['type'] == "circle":
                self.objects.append(Circle(object['center'], object['radius']))
            elif object['type'] == "rectangle":
                self.objects.append(Restangle(object['coordinates']))
            else:
                error_message = f"Unknown type: {object['type']}"
                raise KeyError(error_message)

        self.border = Border(map.border['coordinates'])

    def append(self, point):

        if self.is_complete:
            for object in self.objects:
                if point in object:
                    return object.id

            error_message = f"Unknown point: {point}"
            raise KeyError(error_message)

        else:
            for object in self.objects:
                if point in object:
                    object.append(point)
                    return object.id
            else:
                obj = Undefined(point)
                self.objects.append(Undefined(point))
                return obj.id

    def update(self):

        for i in range(len(self.objects)):
            object = self.objects[i]
            if isinstance(object, Undefined):
                result = object.detected()
                if result:
                    self.objects.append(result)
                    self.objects.remove(object)

        # TODO Baaaaaaaaad!!!!!
        # clean
        for i in range(len(self.objects)):
            undefind = self.objects[i]
            if isinstance(undefind, Undefined):
                for j in range(len(self.objects)):
                    object = self.objects[j]
                    if not isinstance(object, Undefined):

                        if undefind in object:
                            self.objects.remove(object)
                            break

    def save(self):

        for object in self.objects:
            if isinstance(object, Circle):
                self.map.objects[str(object.id)] = {
                    'type': 'circle',
                    'center': object.center,
                    'radius': object.radius,
                }

            elif isinstance(object, Restangle):
                self.map.objects[str(object.id)] = {
                    'type': 'circle',
                    'coordinates': object.coordinates,
                }

        self.map.border['border'] = {
            'type': 'border',
            'coordinates': self.border.coordinates,
        }

        self.map.save()


if __name__ == "__main__":
    cart = Cartographer()
    # ==>
    point = [100, 100]
    cart.append(point)
    cart.append(point)

    cart.update()

    # ==>
    cart.save()
