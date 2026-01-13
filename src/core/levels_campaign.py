from config.settings import Settings
from core.level_config import LevelConfig, TutorialConfig
from pathlib import Path

def create_level_1_config(settings: Settings) -> LevelConfig:
    return LevelConfig(
        name="level_1",
        nest_positions=[(200, 200), (600, 200), (400, 300), (400, 100)],
        initial_counts=[10, 0, 0, 0],
        initial_owners=["ally", "empty", "empty", "empty"],
        tutorial=TutorialConfig(
            title="Básico",
            lines=[
                [("Objetivo: ", (255, 255, 255)), ("DOMINE", (0, 255, 0)), (" os 4 formigueiros.", (255, 255, 255))],
                ["Clique no seu ninho e depois em outro para enviar formigas."],
                [("Segure ", (255, 255, 255)), "SHIFT", (" ao clicar para enviar apenas UMA formiga.", (255, 255, 255))]
            ]
        )
    )