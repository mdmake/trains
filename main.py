from math import radians

import pyglet
import pymunk
from pyglet import shapes
from pyglet.window import key, mouse
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

scene = Scene(space, "configs/field.yaml")
scene.set_scene()

players = []
keys = {}

player = Player(space=space, position=player_position, angle=player_angle)
players.append(player)

key_vector = {"x": 0.0, "y": 0.0, "alpha": 0.0}
target = {"x": width // 2, "y": height // 2}


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
            key_vector["alpha"] = -radians(5.0)

        if key.UP in keys:
            key_vector["v"] = +2
        if key.DOWN in keys:
            key_vector["v"] = -2

        if key.F in keys:
            key_vector["fire_cannon"] = True
        if key.R in keys:
            key_vector["fire_rocket"] = True

        key_vector["target"] = target

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


@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == mouse.LEFT:
        target["x"] = x
        target["y"] = y


@window.event
def on_mouse_release(x, y, button, modifiers):
    pass


# object_count


def draw_visir_lines_and_restrictions(
    laser, generic_color, touch_color, restriction_color
):
    # нарисуем лазер
    for line in laser["restrictions"]["lines"]:
        sprites.append(
            shapes.Line(*line[0], *line[1], 1, color=generic_color, batch=batch)
        )

    for arc in laser["restrictions"]["arcs"]:
        sprites.append(
            shapes.Arc(
                x=arc[0],
                y=arc[1],
                radius=arc[2],
                angle=arc[3],
                start_angle=arc[4],
                color=generic_color,
                batch=batch,
            )
        )

    for ray, measurement in zip(laser["ray"], laser["measurement"]):
        if measurement:
            color = touch_color
            sprites.append(
                shapes.Circle(ray[1][0], ray[1][1], 3, color=touch_color, batch=batch)
            )
        elif laser["alpha_restriction"]:
            color = restriction_color
        else:
            color = generic_color
        sprites.append(shapes.Line(*ray[0], *ray[1], 2, color=color, batch=batch))

    for line in laser["restrictions"]["lines"]:
        sprites.append(
            shapes.Line(*line[0], *line[1], 1, color=generic_color, batch=batch)
        )

    for arc in laser["restrictions"]["arcs"]:
        sprites.append(
            shapes.Arc(
                x=arc[0],
                y=arc[1],
                radius=arc[2],
                angle=arc[3],
                start_angle=arc[4],
                color=generic_color,
                batch=batch,
            )
        )


def draw_cluster_points(clusters):
    import colorsys

    def HSVToRGB(h, s, v):
        (r, g, b) = colorsys.hsv_to_rgb(h, s, v)
        return (int(255 * r), int(255 * g), int(255 * b))

    def getDistinctColors(n):
        huePartition = 1.0 / (n + 1)
        return (HSVToRGB(huePartition * value, 1.0, 1.0) for value in range(0, n))

    color_map = getDistinctColors(len(clusters))

    for color, cluster in zip(color_map, clusters):
        for point in cluster:
            sprites.append(
                shapes.Circle(point[0], point[1], 3, color=color, batch=batch)
            )

        sprites.append(
            shapes.Circle(
                cluster.center[0], cluster.center[1], 3, color=color, batch=batch
            )
        )
        sprites.append(
            shapes.Arc(
                cluster.center[0],
                cluster.center[1],
                cluster.radius,
                color=color,
                batch=batch,
            )
        )


def draw_bullet(bullets):
    for bullet in bullets:
        sprites.append(
            shapes.Circle(bullet["x"], bullet["y"], 5, color=(100, 0, 0), batch=batch)
        )


def draw_rocket(rockets):
    for bullet in rockets:
        sprites.append(
            shapes.Circle(bullet["x"], bullet["y"], 5, color=(100, 0, 0), batch=batch)
        )

    sprites.append(
        shapes.Circle(target["x"], target["y"], 10, color=(255, 0, 0), batch=batch)
    )


def update(dt):
    send_to_train()
    sprites.clear()
    for item in players:
        data = item.step()
        color = (200, 0, 0)

        sprites.append(
            shapes.Circle(
                item.train.from_navigation["x"],
                item.train.from_navigation["y"],
                3,
                color=(200, 0, 200),
                batch=batch,
            )
        )

        # отрисуем точки касания
        for touch_point in list(data["points"]):
            sprites.append(
                shapes.Circle(
                    touch_point[0], touch_point[1], 3, color=item.color, batch=batch
                )
            )

        for line in data["lines"]:
            sprites.append(shapes.Line(*line[0], *line[1], 1, color=color, batch=batch))

        for circle in data["circles"]:
            sprites.append(
                shapes.Arc(
                    circle[0][0], circle[0][1], circle[1], color=color, batch=batch
                )
            )

        for arc in data["arcs"]:
            sprites.append(
                shapes.Arc(
                    x=arc[0],
                    y=arc[1],
                    radius=arc[2],
                    angle=arc[3],
                    start_angle=arc[4],
                    color=color,
                    batch=batch,
                )
            )

        draw_visir_lines_and_restrictions(
            data["laser"],
            generic_color=(124, 252, 0, 125),
            touch_color=(0, 100, 0),
            restriction_color=(0, 255, 127),
        )
        draw_visir_lines_and_restrictions(
            data["locator"],
            generic_color=(221, 160, 221),
            touch_color=(139, 0, 139),
            restriction_color=(238, 0, 238),
        )

        draw_cluster_points(data["clusters"])
        draw_bullet(data["bullets"])
        draw_rocket(data["rockets"])

        item.train_body.angle = item.train.from_navigation["alpha"] - radians(90)
        item.train_body.position = (
            item.train.from_navigation["x"],
            item.train.from_navigation["y"],
        )

    space.step(dt)


if __name__ == "__main__":
    pyglet.clock.schedule_interval(update, 1 / 10.0)
    pyglet.app.run()
