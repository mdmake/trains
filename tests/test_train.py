from game.train import Train

full_config = {
    "tth":
        {
            "v_max": 20,
            "max_angle_speed": 5,
        },
    "private":
        {
            "place": [5, 15]
        }

}


def test_create_object_from_file_config():
    train = Train('test', "configs/train.yaml")
    assert train is not None


def test_create_object_from_dict_config():
    train = Train('test', full_config)
    assert train is not None
