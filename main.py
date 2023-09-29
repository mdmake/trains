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
        player.train.angle += radians(5)
    if key_handler[key.E]:
        player.train.angle -= radians(5)

    if key_handler[key.SPACE]:
        player.train.v = 0.0

    if key_handler[key.B]:
        player.train.v = 5.0

    info = player.update()

    current_touch_points = set(info['maps'])
    new_touch_points = list(current_touch_points - touch_points)
    for touch_point in new_touch_points:
        sprites.append(shapes.Circle(touch_point[0], touch_point[1], 3, color=(0, 255, 0), batch=batch))

    space.step(dt)


if __name__ == '__main__':
    pyglet.clock.schedule_interval(update, 1 / 60.0)
    pyglet.app.run()
