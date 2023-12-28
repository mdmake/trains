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
# scene.set_default_scene(space=space, width=width, height=height, margin=20)

players = []

player = Player(
    space=space,
    position=player_position,
    angle=player_angle
)
players.append(player)

key_vector = {"x": 0.0, "y": 0.0, "alpha": 0.0}


# bot = Player(
#     space=space,
#     position=(600., 600.),
#     angle=-player_angle,
#     name="bot",
#     color=(0, 255, 0)
# )
#
# players.append(bot)
#
# bot_2 = Player(
#     space=space,
#     position=(700, 200),
#     angle=-player_angle + radians(30),
#     name="bot_2",
#     color=(255, 160, 0)
# )
#
# players.append(bot_2)


@window.event
def on_draw():
    window.clear()
    space.debug_draw(options)
    batch.draw()


@window.event
def on_key_press(symbol, modifiers):
    step = 10
    angle_step = 5

    # if not player.train.auto:
    #     if symbol == key.LEFT:

    #         key_vector["x"] = -step
    #     if symbol == key.RIGHT:
    #         key_vector["x"] = step
    #     if symbol == key.UP:
    #         key_vector["y"] = step
    #     if symbol == key.DOWN:
    #         key_vector["y"] = -step
    #     if symbol == key.Q:
    #         key_vector["alpha"] = radians(angle_step)
    #     if symbol == key.E:
    #         key_vector["alpha"] = -radians(angle_step)
    #
    # if symbol == key.SPACE:
    #     if player.train.auto:
    #         for item in players:
    #             item.train.v = 0.0
    #             item.train.auto = False
    #     else:
    #         for item in players:
    #             item.train.v = 5.0
    #             item.train.auto = True


@window.event
def on_key_release(symbol, modifiers):
    # if not player.train.auto:
    #     if symbol == key.LEFT or symbol == key.RIGHT:
    #         key_vector["x"] = 0
    #     if symbol == key.UP or symbol == key.DOWN:
    #         key_vector["y"] = 0
    #     if symbol == key.Q or symbol == key.E:
    #         key_vector["alpha"] = 0
    pass


# object_count


def draw_ll(laser, generic_color, touch_color, restriction_color):
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
    sprites.clear()

    for item in players:

        data = item.step()
        color = (200, 0, 0)
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

        draw_ll(
            data['laser'], generic_color=(124, 252, 0, 125), touch_color=(0, 100, 0), restriction_color=(0, 255, 127)
        )
        draw_ll(
            data['locator'], generic_color=(221, 160, 221), touch_color=(139, 0, 139), restriction_color=(238, 0, 238)
        )

    space.step(dt)


if __name__ == '__main__':
    pyglet.clock.schedule_interval(update, 1 / 10.0)
    pyglet.app.run()
