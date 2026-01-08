from typing import List, Tuple


class Settings:
    WIDTH = 800
    HEIGHT = 400
    FPS = 60
    SPEED = 4
    NEST_SIZE = (64, 64)
    ANT_SIZE = (48, 48)
    WINDOW_TITLE = "Ant Simulator"

    # Assets base paths
    ASSETS_DIR = "ant_simulator/assets"
    SPRITES_DIR = f"{ASSETS_DIR}/sprites"
    ANTS_DIR = f"{SPRITES_DIR}/ants"
    STRUCTURES_DIR = f"{SPRITES_DIR}/structures"

    # Colors
    BG_COLOR = (30, 30, 30)
    TEXT_COLOR = (255, 255, 255)
    SELECTION_COLOR = (255, 255, 0)

    # UI/animation
    FONT_SIZE = 32
    ANIM_INTERVAL_MS = 165

    # Configuração dos ninhos, suas posições iniciais e contagens de formigas
    NEST_POSITIONS: List[Tuple[int, int]] = [(200, 200), (600, 200), (400, 300), (400, 100)]
    INITIAL_ANTS_PER_NEST: List[int] = [1, 0, 1, 5]
    # Se verdadeiro, embaralha as posições dos ninhos a cada execução
    RANDOMIZE_NEST_POSITIONS: bool = True
