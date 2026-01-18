from src.config.settings import Settings
from src.core.level_config import LevelConfig, TutorialConfig

# Caminho para o ícone SHIFT (ajuste conforme seu path real)
IMG_SHIFT = Settings.ASSETS_DIR / "sprites" / "buttons" / "shift.png"
IMG_CTRL = Settings.ASSETS_DIR / "sprites" / "buttons" / "ctrl.png"


def create_intro_config(settings: Settings) -> LevelConfig:
    return LevelConfig(
        name="intro",
        nest_positions=[
            (200, 300),  # Esquerda
            (600, 300),  # Direita
            (400, 450),  # Baixo
            (400, 150),  # Cima
        ],
        initial_counts=[10, 0, 0, 0],
        initial_owners=["ally", "empty", "empty", "empty"],
        tutorial=TutorialConfig(
            title="Básico",
            lines=[
                [
                    ("Objetivo: ", (255, 255, 255)),
                    ("DOMINE", (0, 255, 0)),
                    (" os 4 formigueiros.", (255, 255, 255)),
                ],
                ["Clique no seu ninho e depois em outro para enviar formigas."],
                [
                    ("Segure ", (255, 255, 255)),
                    IMG_SHIFT,
                    (" ao clicar para enviar apenas UMA formiga.", (255, 255, 255)),
                ],
                [
                    ("Segure ", (255, 255, 255)),
                    IMG_CTRL,
                    (
                        " ao clicar para selecionar mais de um formigueiro.",
                        (255, 255, 255),
                    ),
                ],
            ],
        ),
    )


def create_intro2_config(settings: Settings) -> LevelConfig:
    return LevelConfig(
        name="intro2",
        nest_positions=[(250, 250), (550, 250), (400, 120)],
        initial_counts=[8, 8, 6],
        initial_owners=["ally", "ally", "enemy"],
        tutorial=TutorialConfig(
            title="Primeiro Conflito",
            lines=[
                ["Cuidado! Há inimigos no mapa."],
                [
                    ("Objetivo: ", (255, 255, 255)),
                    ("DOMINE", (0, 255, 0)),
                    (" o ", (255, 255, 255)),
                    ("formigueiro inimigo", (255, 0, 0)),
                    (".", (255, 255, 255)),
                ],
                ["Acumule forças antes de atacar."],
            ],
        ),
    )


def create_intro3_config(settings: Settings) -> LevelConfig:
    return LevelConfig(
        name="intro3",
        nest_positions=[
            (150, 300),  # Esquerda Centro
            (400, 150),  # Centro Cima
            (400, 450),  # Centro Baixo
            (650, 300),  # Direita Centro
        ],
        initial_counts=[10, 0, 0, 10],
        initial_owners=["ally", "empty", "empty", "enemy"],
        enemy_produces=True,
        tutorial=TutorialConfig(
            title="Guerra Total",
            lines=[
                ["O inimigo agora produz novas formigas."],
                ["O inimigo tentará dominar todos os formigueiros."],
                ["Seja rápido para capturar os ninhos vazios no centro."],
                [("Capture tudo para vencer.", (255, 255, 255))],
            ],
        ),
    )
