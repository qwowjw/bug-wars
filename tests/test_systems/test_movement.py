from systems.movement import MovementSystem
from entities.ant import Ant


def test_ant_moves_forward():
    ant = Ant((0, 0))
    ant.dir = (1, 0)
    ant.speed = 10
    MovementSystem().update_ant(ant, 1.0)
    assert ant.pos[0] == 10
    assert ant.pos[1] == 0
