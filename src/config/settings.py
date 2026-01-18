import logging
from typing import List, Tuple
from pathlib import Path


class Settings:
    # --- Configurações de Display ---
    WIDTH: int = 800
    HEIGHT: int = 600
    FPS: int = 60

    # --- Configurações de Gameplay ---
    SPEED: int = 4
    NEST_SIZE: Tuple[int, int] = (64, 64)
    ANT_SIZE: Tuple[int, int] = (48, 48)
    WINDOW_TITLE: str = "Ant Simulator"

    # --- Configurações de Cores ---
    BG_COLOR: Tuple[int, int, int] = (30, 30, 30)
    TEXT_COLOR: Tuple[int, int, int] = (255, 255, 255)
    SELECTION_COLOR: Tuple[int, int, int] = (255, 255, 0)
    UI_COLOR: Tuple[int, int, int] = (200, 200, 200)

    # --- Configurações de UI/Animação ---
    FONT_SIZE: int = 32
    ANIM_INTERVAL_MS: int = 165
    ANT_SPACING_PX: int = 12

    # --- Configurações de Caminhos (Pathing Robusto) ---
    # Base dir é a pasta onde está este arquivo (src/config)
    _CURRENT_DIR = Path(__file__).resolve().parent
    # Project root (src/config -> src -> root)
    # Ajuste .parent quantas vezes for necessário para chegar na raiz do projeto
    PROJECT_ROOT = _CURRENT_DIR.parent.parent

    # Tenta localizar a pasta assets em locais comuns
    # 1. Dentro de src/assets (estrutura de pacote)
    # 2. Na raiz do projeto/assets (estrutura de repo)
    ASSETS_DIR: Path = PROJECT_ROOT / "assets"

    # Se a pasta assets estiver dentro de src, descomente a linha abaixo:
    # ASSETS_DIR = _CURRENT_DIR.parent / "assets"

    # Subdiretórios usando path joining seguro
    SPRITES_DIR: Path = ASSETS_DIR / "sprites"
    ANTS_DIR: Path = SPRITES_DIR / "ants"
    STRUCTURES_DIR: Path = SPRITES_DIR / "structures"

    # --- Caminhos de UI ---
    UI_DIR: Path = SPRITES_DIR / "ui"
    IMG_STAR_YELLOW: Path = UI_DIR / "yellow_star.png"
    IMG_STAR_BLACK: Path = UI_DIR / "black_star.png"
    
    # --- Configurações de Ninhos/Colônias ---
    NEST_POSITIONS: List[Tuple[int, int]] = [
        (200, 200),
        (600, 200),
        (400, 300),
        (400, 100),
    ]
    INITIAL_ANTS_PER_NEST: List[int] = [10, 0, 10, 5]
    DEFAULT_ANT_TYPE_NAME: str = "Farao"
    INITIAL_ANT_TYPE_PER_NEST: List[str] = [DEFAULT_ANT_TYPE_NAME] * len(NEST_POSITIONS)
    RANDOMIZE_NEST_POSITIONS: bool = True

    # --- Configurações de Sistema ---
    LOG_LEVEL: int = logging.INFO
    THREAD_WORKERS: int = 2

    UI_ICON_SCALE: float = 1.5  # Escala para ícones de UI
