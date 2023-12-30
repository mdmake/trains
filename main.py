from math import radians

import pyglet
import pymunk
from pyglet import shapes
from pyglet.window import key
from pymunk.pyglet_util import DrawOptions

from game.dispatcher import Player
from game.scene import Scene

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

scene = Scene(space, 'configs/field.yaml')
scene.set_scene()

players = []
keys = {}

player = Player(
    space=space,
    position=player_position,
    angle=player_angle
)
players.append(player)

key_vector = {"x": 0.0, "y": 0.0, "alpha": 0.0}


@window.event
def on_draw():
    window.clear()
    space.debug_draw(options)
    batch.draw()


@window.event
def on_key_press(symbol, modifiers):
    if not player.train.train.auto:
        keys[symbol] = True


def send_to_train():
    key_vector = {}
    if not player.train.train.auto:
        if key.LEFT in keys:
            key_vector["alpha"] = radians(5.0)
        elif key.RIGHT in keys:
            key_vector["alpha"] = - radians(5.0)

        if key.UP in keys:
            key_vector["v"] = +2
        if key.DOWN in keys:
            key_vector["v"] = -2

        player.train.train.external(**key_vector)


@window.event
def on_key_release(symbol, modifiers):
    if symbol in keys:
        del keys[symbol]

    if symbol == key.SPACE:
        if player.train.train.auto:
            for item in players:
                item.train.train.auto = False
                player.train.train.external(v=0)

        else:
            for item in players:
                item.train.train.auto = True


# object_count


def draw_visir_lines_and_restrictions(laser, generic_color, touch_color, restriction_color):
    # нарисуем лазер
    for line in laser['restrictions']["lines"]:
        sprites.append(shapes.Line(*line[0], *line[1], 1, color=generic_color, batch=batch))

    for arc in laser['restrictions']["arcs"]:
        sprites.append(
            shapes.Arc(x=arc[0], y=arc[1], radius=arc[2], angle=arc[3], start_angle=arc[4], color=generic_color,
                       batch=batch))

    for ray, measurement in zip(laser['ray'], laser["measurement"]):

        if measurement:
            color = touch_color
            sprites.append(shapes.Circle(ray[1][0], ray[1][1], 3, color=touch_color, batch=batch))
        elif laser["alpha_restriction"]:
            color = restriction_color
        else:
            color = generic_color
        sprites.append(shapes.Line(*ray[0], *ray[1], 2, color=color, batch=batch))

    for line in laser['restrictions']["lines"]:
        sprites.append(shapes.Line(*line[0], *line[1], 1, color=generic_color, batch=batch))

    for arc in laser['restrictions']["arcs"]:
        sprites.append(
            shapes.Arc(x=arc[0], y=arc[1], radius=arc[2], angle=arc[3], start_angle=arc[4], color=generic_color,
                       batch=batch))


def update(dt):
    send_to_train()
    sprites.clear()
    for item in players:

        data = item.step()
        color = (200, 0, 0)

        sprites.append(
            shapes.Circle(item.train.from_navigation["x"], item.train.from_navigation["y"], 3, color=(200, 0, 200),
                          batch=batch))

        # отрисуем точки касания
        for touch_point in list(data['points']):
            sprites.append(shapes.Circle(touch_point[0], touch_point[1], 3, color=item.color, batch=batch))

        for line in data["lines"]:
            sprites.append(shapes.Line(*line[0], *line[1], 1, color=color, batch=batch))

        for circle in data["circles"]:
            sprites.append(shapes.Arc(circle[0][0], circle[0][1], circle[1], color=color, batch=batch))

        for arc in data["arcs"]:
            sprites.append(shapes.Arc(x=arc[0], y=arc[1], radius=arc[2], angle=arc[3], start_angle=arc[4], color=color,
                                      batch=batch))

        draw_visir_lines_and_restrictions(
            data['laser'], generic_color=(124, 252, 0, 125), touch_color=(0, 100, 0), restriction_color=(0, 255, 127)
        )
        draw_visir_lines_and_restrictions(
            data['locator'], generic_color=(221, 160, 221), touch_color=(139, 0, 139), restriction_color=(238, 0, 238)
        )

        item.train_body.angle = item.train.from_navigation["alpha"] - radians(90)
        item.train_body.position = item.train.from_navigation["x"], item.train.from_navigation["y"]

    space.step(dt)


if __name__ == '__main__':
    pyglet.clock.schedule_interval(update, 1 / 10.0)
    pyglet.app.run()
