from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class AntType:
    name: str
    armor: float = 0.0
    poison_resistance: float = 0.0
    range: float = 8.0
    dps: float = 1.0
    special_effect: Optional[Dict[str, Any]] = field(default_factory=dict)
    aggressiveness: float = 0.5
    production_time: float = 10.0
    speed: float = 60.0
    crit_chance: float = 0.05
    crit_multiplier: float = 1.5


class Ant:
    def __init__(self, pos, ant_type: Optional[AntType] = None):
        self.x, self.y = pos
        self.dir = (1.0, 0.0)

        # If provided, initialize stats from AntType, otherwise use defaults
        if ant_type is None:
            ant_type = AntType(name="generic")

        self.type = ant_type
        self.speed = float(ant_type.speed)
        self.armor = float(ant_type.armor)
        self.poison_resistance = float(ant_type.poison_resistance)
        self.attack_range = float(ant_type.range)
        self.dps = float(ant_type.dps)
        self.special_effect = ant_type.special_effect or {}
        self.aggressiveness = float(ant_type.aggressiveness)
        self.production_time = float(ant_type.production_time)
        self.crit_chance = float(ant_type.crit_chance)
        self.crit_multiplier = float(ant_type.crit_multiplier)

    @property
    def pos(self):
        return (self.x, self.y)

    def __repr__(self):
        return f"Ant(type={self.type.name}, pos=({self.x:.1f},{self.y:.1f}))"
