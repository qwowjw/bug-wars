from entities.ant_types import ALL_ANT_TYPES
from entities.ant import Ant


def test_all_ant_types_instantiable():
    for t in ALL_ANT_TYPES:
        a = Ant((1, 2), t)
        assert a.type is t
        assert isinstance(a.dps, float)
        assert isinstance(a.speed, float)
        assert isinstance(a.armor, float)
        assert isinstance(a.aggressiveness, float)
        assert isinstance(a.production_time, float)
        assert isinstance(a.crit_chance, float)
        assert isinstance(a.crit_multiplier, float)
        # special_effect must be a dict or empty
        assert isinstance(a.special_effect, dict)
