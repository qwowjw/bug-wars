from entities.ant import Ant
from utils.math_utils import clamp


class MovementSystem:
    def update_ant(self, ant: Ant, dt: float):
        dx = ant.dir[0] * ant.speed * dt
        dy = ant.dir[1] * ant.speed * dt
        ant.x += dx
        ant.y += dy
        ant.x = clamp(ant.x, 0, 2000)  # world bounds placeholder
        ant.y = clamp(ant.y, 0, 2000)
