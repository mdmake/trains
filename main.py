import pyglet
import pymunk
from pyglet import shapes
from pyglet.window import key
from pymunk.pyglet_util import DrawOptions

from game.scene import Scene
from game.player import Player

from math import radians, atan2, cos, sin, sqrt

width = 1280
height = 720

player_angle = radians(45)
player_position = width // 2, height // 2

window = pyglet.window.Window(width, height)
pyglet.gl.glClearColor(1, 1, 1, 1)

options = DrawOptions()
batch = pyglet.graphics.Batch()

key_handler = key.KeyStateHandler()
window.push_handlers(key_handler)
space = pymunk.Space()
space.gravity = 0, -1000

handler = space.add_default_collision_handler()

touch_points = set()
sprites = []

scene = Scene()
scene.set_default_scene(space=space, width=width, height=height, margin=20)

player = Player(
    space=space,
    position=player_position,
    angle=player_angle
)

bot = Player(
    space=space,
    position=(600, 600),
    angle=-player_angle,
    name="bot",
    color=(0, 255, 0)
)

players = [player, bot]


@window.event
def on_draw():
    window.clear()
    space.debug_draw(options)
    batch.draw()


def update(dt):
    if key_handler[key.LEFT]:
        player.position = player.position[0] - 10, player.position[1]
    if key_handler[key.RIGHT]:
        player.position = player.position[0] + 10, player.position[1]
    if key_handler[key.UP]:
        player.position = player.position[0], player.position[1] + 10
    if key_handler[key.DOWN]:
        player.position = player.position[0], player.position[1] - 10

    if key_handler[key.Q]:
        player.train.alpha += radians(5)
    if key_handler[key.E]:
        player.train.alpha -= radians(5)

    if key_handler[key.SPACE]:
        for item in players:
            item.train.v = 0.0

    if key_handler[key.B]:
        for item in players:
            item.train.v = 5.0

    for item in players:

        data = item.update()

        # отрисуем точки касания
        for touch_point in list(data['new_touch_points']):
            sprites.append(shapes.Circle(touch_point[0], touch_point[1], 3, color=item.train.color, batch=batch))

    space.step(dt)


if __name__ == '__main__':
    pyglet.clock.schedule_interval(update, 1 / 60.0)
    pyglet.app.run()
