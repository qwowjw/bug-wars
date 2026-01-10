from .ant import Ant, AntType
from .nest import Nest
from typing import Optional


class Colony:
    def __init__(self, nest_pos, ant_type: Optional[AntType] = None):
        self.nest = Nest(nest_pos)
        self.ants = []
        # Optional default type for newly produced ants
        self.default_ant_type: Optional[AntType] = ant_type
        # production tracking (seconds)
        self.production_progress: float = 0.0

    def spawn_ant(self, pos=None, ant_type: Optional[AntType] = None):
        if pos is None:
            pos = self.nest.pos
        chosen_type = ant_type or self.default_ant_type
        ant = Ant(pos, chosen_type)
        self.ants.append(ant)
        return ant

    def spawn_ants(self, count: int, pos=None, ant_type: Optional[AntType] = None):
        """Gera várias formigas no ninho e retorna a lista criada."""
        created = []
        for _ in range(count):
            created.append(self.spawn_ant(pos, ant_type))
        return created

    def remove_ant(self):
        """Remove e retorna uma formiga do ninho (se houver), ou None caso contrário."""
        if not self.ants:
            return None
        return self.ants.pop()

    def update(self, dt: float) -> int:
        """Atualiza produção no ninho.

        dt: delta time em segundos
        Retorna o número de formigas produzidas neste passo.
        """
        produced = 0
        # Determina tempo de produção baseado no tipo de formiga padrão
        ant_type = self.default_ant_type
        if not ant_type and self.ants:
            # usa o tipo da primeira formiga, se disponível
            ant_type = getattr(self.ants[0], "type", None)

        if ant_type is None:
            return produced

        production_time = float(getattr(ant_type, "production_time", 0.0))
        if production_time <= 0.0:
            return produced

        # Se houver ao menos uma formiga, acumula progresso
        if len(self.ants) > 0:
            self.production_progress += dt

        while self.production_progress >= production_time:
            self.production_progress -= production_time
            # produz nova formiga do mesmo tipo
            self.spawn_ant(self.nest.pos, ant_type)
            produced += 1

        return produced
