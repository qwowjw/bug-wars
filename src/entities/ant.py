class Ant:
    def __init__(self, pos):
        self.x, self.y = pos
        self.speed = 60.0  # px/s
        self.dir = (1.0, 0.0)

    @property
    def pos(self):
        return (self.x, self.y)
