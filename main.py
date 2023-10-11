import pyglet
import pymunk
from pyglet import shapes
from pyglet.window import key
from pymunk.pyglet_util import DrawOptions

from game.scene import Scene
from game.player import Player

from math import radians

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
sprites = []

scene = Scene()
scene.set_default_scene(space=space, width=width, height=height, margin=20)

players = []

player = Player(
    space=space,
    position=player_position,
    angle=player_angle
)
players.append(player)

key_vector = {"x": 0.0, "y": 0.0, "alpha": 0.0}

bot = Player(
    space=space,
    position=(600., 600.),
    angle=-player_angle,
    name="bot",
    color=(0, 255, 0)
)

players.append(bot)

bot_2 = Player(
    space=space,
    position=(700, 200),
    angle=-player_angle + radians(30),
    name="bot_2",
    color=(255, 160, 0)
)

players.append(bot_2)


@window.event
def on_draw():
    window.clear()
    space.debug_draw(options)
    batch.draw()


@window.event
def on_key_press(symbol, modifiers):
    step = 10
    angle_step = 5

    if not player.train.auto:
        if symbol == key.LEFT:
            key_vector["x"] = -step
        if symbol == key.RIGHT:
            key_vector["x"] = step
        if symbol == key.UP:
            key_vector["y"] = step
        if symbol == key.DOWN:
            key_vector["y"] = -step
        if symbol == key.Q:
            key_vector["alpha"] = radians(angle_step)
        if symbol == key.E:
            key_vector["alpha"] = -radians(angle_step)

    if symbol == key.SPACE:
        if player.train.auto:
            for item in players:
                item.train.v = 0.0
                item.train.auto = False
        else:
            for item in players:
                item.train.v = 5.0
                item.train.auto = True


@window.event
def on_key_release(symbol, modifiers):
    if not player.train.auto:
        if symbol == key.LEFT or symbol == key.RIGHT:
            key_vector["x"] = 0
        if symbol == key.UP or symbol == key.DOWN:
            key_vector["y"] = 0
        if symbol == key.Q or symbol == key.E:
            key_vector["alpha"] = 0


def update(dt):
    if not player.train.auto:
        player.train.manual_update(*[key_vector[k] for k in ["x", "y", "alpha"]])
    else:
        key_vector[0] = 0
        key_vector[1] = 0
        key_vector[2] = 0

    for item in players:

        data = item.update()

        # отрисуем точки касания
        for touch_point in list(data['new_touch_points']):
            sprites.append(shapes.Circle(touch_point[0], touch_point[1], 3, color=item.train.color, batch=batch))

        for polyline in data["lines"]:
            for i in range(len(polyline[:-1])):
                sprites.append(shapes.Line(*polyline[i], *polyline[i+1], 3, color=item.train.color, batch=batch))

        for circle in data["circles"]:
            sprites.append(shapes.Arc(circle[0][0], circle[0][1], circle[1], color=item.train.color, batch=batch))

    space.step(dt)


if __name__ == '__main__':
    pyglet.clock.schedule_interval(update, 1 / 60.0)
    pyglet.app.run()
