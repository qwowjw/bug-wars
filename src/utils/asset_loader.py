import logging
from typing import Optional, Union
from pathlib import Path
import pygame


def load_image(path: Union[str, Path]) -> Optional[pygame.Surface]:
    """
    Carrega uma imagem de forma segura.
    Retorna None e loga um aviso se falhar.

    Args:
        path: Caminho absoluto ou relativo para a imagem.

    Returns:
        pygame.Surface convertido com alpha se sucesso, None caso contrário.
    """
    logger = logging.getLogger(__name__)

    # Converte para objeto Path se for string
    target_path = Path(path)

    # Verifica existência
    if not target_path.exists():
        logger.error(f"IMAGEM NÃO ENCONTRADA: {target_path.absolute()}")
        return None

    try:
        surface = pygame.image.load(str(target_path))
        # convert_alpha é crucial para performance e transparência
        return surface.convert_alpha()
    except pygame.error as e:
        logger.error(f"Erro do Pygame ao carregar {target_path}: {e}")
        return None
    except Exception:
        logger.exception(f"Erro inesperado ao carregar {target_path}")
        return None
