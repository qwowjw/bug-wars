from entities.nest import Nest


def test_nest_position():
    n = Nest((10, 20))
    assert n.pos == (10, 20)
