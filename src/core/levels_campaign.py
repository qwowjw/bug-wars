from src.config.settings import Settings
from src.core.level_config import LevelConfig, TutorialConfig
from src.core.nest_types import star_positions

# Imports necessários para tipagem e configuração
from src.entities.ant_types import Quenquen, farao
from src.ai.enemy_controller import AI_BALANCED


def create_level_1_config(settings: Settings) -> LevelConfig:
    center = (settings.WIDTH // 2, settings.HEIGHT // 2)

    star_nests = star_positions(center=center, radius=120, points=5)

    # Montamos a lista de posições
    all_positions = [center] + star_nests

    # Montamos a lista de donos
    # Centro: Ally | Pontas 1,2: Empty | Pontas 3,4,5: Enemy
    owners = ["ally", "empty", "empty", "ally", "enemy", "enemy"]

    # Montamos a lista de counts
    counts = [10, 0, 0, 10, 10, 10]

    # --- AQUI ESTÁ O SEGREDO DOS TIPOS ---
    # Precisamos de uma lista de strings com o nome do tipo para CADA ninho.
    # Ally (índice 0) usa Farao.
    # Empty (índices 1,2) usam Farao (padrão).
    # Enemy (índices 3,4,5) usam Quenquen.

    # Podemos criar a lista manualmente:
    # types_list = ["Farao", "Farao", "Farao", "Quenquen", "Quenquen", "Quenquen"]

    # Ou programaticamente para garantir consistência com a lista de owners:
    types_list = []
    for owner in owners:
        if owner == "enemy":
            types_list.append(Quenquen.name)  # Usa o nome "Quenquen"
        else:
            types_list.append(farao.name)  # Usa o nome "Farao"

    return LevelConfig(
        name="level_1_invasion",
        nest_positions=all_positions,
        initial_counts=counts,
        initial_owners=owners,
        # Define os tipos específicos para carregar os atributos e assets corretos
        ant_types=types_list,
        # Define que o inimigo produz novas formigas
        enemy_produces=True,
        # Define a Inteligência Artificial deste nível
        ai_profile=AI_BALANCED,
        tutorial=TutorialConfig(
            title="Invasão Quenquen",
            lines=[
                ["Os invasores Quenquen chegaram!"],
                ["Eles são agressivos e tentam expandir rápido."],
            ],
        ),
    )
