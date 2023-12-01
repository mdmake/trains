from game.train import Train


def test_create_object():
    train = Train(0.0, (0.0, 0.0))
    assert train is not None


def test_always_fails():
    assert True
