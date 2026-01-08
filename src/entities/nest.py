class Nest:
    def __init__(self, pos):
        self.x, self.y = pos
        self.selected = False

    @property
    def pos(self):
        return (self.x, self.y)
