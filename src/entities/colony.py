from .ant import Ant
from .nest import Nest


class Colony:
    def __init__(self, nest_pos):
        self.nest = Nest(nest_pos)
        self.ants = []

    def spawn_ant(self, pos=None):
        if pos is None:
            pos = self.nest.pos
        ant = Ant(pos)
        self.ants.append(ant)
        return ant

    def spawn_ants(self, count: int, pos=None):
        """Gera várias formigas no ninho e retorna a lista criada."""
        created = []
        for _ in range(count):
            created.append(self.spawn_ant(pos))
        return created

    def remove_ant(self):
        """Remove e retorna uma formiga do ninho (se houver), ou None caso contrário."""
        if not self.ants:
            return None
        return self.ants.pop()
