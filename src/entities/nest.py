from typing import Tuple


class Nest:
    def __init__(self, pos: Tuple[int, int]) -> None:
        self.x, self.y = pos
        self.selected = False

    @property
    def pos(self) -> Tuple[int, int]:
        return (self.x, self.y)
