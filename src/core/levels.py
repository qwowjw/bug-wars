from typing import List, Tuple

from config.settings import Settings
from core.level_scene import LevelConfig
from entities.ant_types import ANT_TYPES_BY_NAME


Vec2 = Tuple[int, int]

def create_intro_config(settings: Settings) -> LevelConfig:
    """Cria a configuração do nível introdutório.
    
    Args:
        settings: Configurações globais do jogo.
        
    Returns:
        Configuração do nível introdutório com 4 ninhos, apenas o primeiro
        pertencendo ao jogador com 10 formigas.
    """
    positions: List[Vec2] = [
        (200, 200),
        (600, 200),
        (400, 300),
        (400, 100),
    ]
    return LevelConfig(
        name="intro",
        nest_positions=positions,
        initial_counts=[10, 0, 0, 0],
        initial_owners=["ally", "empty", "empty", "empty"],
        ant_types=[settings.DEFAULT_ANT_TYPE_NAME] * len(positions),
        randomize_positions=False,
        enemy_produces=False,
        victory_condition=None,
    )


def create_level1_config(settings: Settings) -> LevelConfig:
    """Cria a configuração do primeiro nível.
    
    Args:
        settings: Configurações globais do jogo.
        
    Returns:
        Configuração do nível 1 com 3 ninhos, 2 aliados e 1 inimigo.
    """
    positions: List[Vec2] = [
        (250, 250),
        (550, 250),
        (400, 120),
    ]
    return LevelConfig(
        name="level1",
        nest_positions=positions,
        initial_counts=[8, 8, 6],
        initial_owners=["ally", "ally", "enemy"],
        ant_types=[settings.DEFAULT_ANT_TYPE_NAME] * len(positions),
        randomize_positions=False,
        enemy_produces=False,
        victory_condition=None,
    )


def create_level2_config(settings: Settings) -> LevelConfig:
    """Cria a configuração do segundo nível.
    
    Layout em diamante: esquerda (jogador com 10 Faraó), topo vazio,
    base vazio, direita inimigo (Quenquen com 10).
    
    Args:
        settings: Configurações globais do jogo.
        
    Returns:
        Configuração do nível 2 com layout em diamante e inimigo produzindo formigas.
    """
    positions: List[Vec2] = [
        (150, 250),
        (350, 120),
        (350, 300),
        (550, 250),
    ]
    return LevelConfig(
        name="level2",
        nest_positions=positions,
        initial_counts=[10, 0, 0, 10],
        initial_owners=["ally", "empty", "empty", "enemy"],
        ant_types=[
            settings.DEFAULT_ANT_TYPE_NAME,
            settings.DEFAULT_ANT_TYPE_NAME,
            settings.DEFAULT_ANT_TYPE_NAME,
            "Quenquen",
        ],
        randomize_positions=False,
        enemy_produces=True,
        victory_condition=None,
    )