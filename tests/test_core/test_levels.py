from config.settings import Settings
from core.levels_intro import (
    create_intro_config,
    create_intro2_config,
    create_intro3_config,
)
from core.level_scene import default_victory_condition


def test_intro_config_structure():
    settings = Settings()
    cfg = create_intro_config(settings)
    assert cfg.name == "intro"
    assert len(cfg.nest_positions) == 4
    assert len(cfg.initial_counts) == 4
    assert len(cfg.initial_owners) == 4


def test_intro2_config_triangle():
    settings = Settings()
    cfg = create_intro2_config(settings)
    assert cfg.name == "intro2"
    assert len(cfg.nest_positions) == 3
    assert cfg.initial_owners.count("ally") == 2


def test_intro3_config_diamond():
    settings = Settings()
    cfg = create_intro3_config(settings)
    assert cfg.name == "intro3"
    assert len(cfg.nest_positions) == 4
    assert cfg.initial_owners.count("ally") == 1
    assert cfg.initial_owners.count("enemy") == 1


def test_default_victory():
    owners = ["ally", "ally", "ally"]
    assert default_victory_condition(owners, []) is True
    owners = ["ally", "enemy", "ally"]
    assert default_victory_condition(owners, []) is False
