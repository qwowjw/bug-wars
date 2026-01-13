import math
from typing import List, Tuple

Vec2 = Tuple[int, int]


def star_positions(center: Vec2, radius: int, points: int = 5) -> List[Vec2]:
    """
    Gera posições em forma de estrela (pontas externas).
    """
    cx, cy = center
    angle_step = 2 * math.pi / points

    positions: List[Vec2] = []
    for i in range(points):
        angle = i * angle_step - math.pi / 2
        x = int(cx + radius * math.cos(angle))
        y = int(cy + radius * math.sin(angle))
        positions.append((x, y))

    return positions
