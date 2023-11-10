import yaml
from datetime import date


class Map:

    def __init__(self, complete=0):
        self._complete = complete
        self.objects = dict()
        self.description = dict()
        self.border = dict()
        self.path = None

    @property
    def complete(self):
        return True if self._complete >= 100 else False


    def set_path(self, path):
        self.path = path


    def load(self, filename):
        with open(filename, 'r') as f:
            data = yaml.safe_load(f)
            self.border = data['border']
            self.objects = data['objects']
            self.description = data['description']
            self._complete = self.description['complete']

    def save(self, path=None, map_name=None, text=None):
        # TODO - add minutes and hours

        path = path or self.path
        self.description['date'] = date.today().strftime("%H:%M %d.%m.%Y")
        self.description['map_name'] = map_name or self.description.get('map_name',
                                                                        f"The map was created {self.description['date']}")

        self.description['text'] = text or self.description.get('text', 'no text')

        with open(path, 'w') as file:
            data = dict(
                {
                    "description": self.description,
                    "border": self.border,
                    "objects": self.objects,
                }
            )
            yaml.dump(data, file)




class Navigator:
    """
    path from A to B
    """
    pass


if __name__ == "__main__":
    mp = Map()
    mp.load("../configs/field.yaml")
    mp.save("../configs/field_1.yaml", text='my first map')
