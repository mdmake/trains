from game.cartographer import Cartographer


def test_creation():
    points = [
        (5, 5),
        (5, 6),
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (6, 5),
        (6, 6),
        (100, 100),
        (200, 200),
    ]
    cartographer = Cartographer()
    cartographer.append(points)
    assert len(cartographer.clusters) == 3

    new_points = [(i * 5, i * 5) for i in range(21)]
    cartographer.append(new_points)
    cartographer.update()

    assert len(cartographer.clusters) == 2
