import pygame
from typing import List, Tuple
from pathlib import Path
from utils.asset_loader import load_image
from config.settings import Settings
from core.level_config import InstructionElement


def render_rich_text_line(
    surface: pygame.Surface,
    elements: List[InstructionElement],
    start_pos: Tuple[int, int],
    font: pygame.font.Font,
) -> int:
    """
    Renderiza uma linha contendo texto (com cores variadas) e imagens (ícones).
    Retorna a altura máxima desenhada na linha para calcular o próximo espaçamento.
    """
    x, y = start_pos
    max_height = 0

    for elem in elements:
        # Caso 1: Caminho para Imagem (Ícone)
        if isinstance(elem, Path):
            img = load_image(elem)
            if img:
                # Escala ícone para caber na altura da fonte (aprox)
                target_h = int(font.get_height() * Settings.UI_ICON_SCALE)
                aspect = img.get_width() / img.get_height()
                target_w = int(target_h * aspect)
                scaled = pygame.transform.smoothscale(img, (target_w, target_h))

                rect = scaled.get_rect(topleft=(x, y))
                surface.blit(scaled, rect)
                x += rect.width + 5
                max_height = max(max_height, rect.height)
            continue

        # Caso 2: Texto
        text = ""
        color = Settings.TEXT_COLOR

        if isinstance(elem, tuple):
            text, color = elem
        elif isinstance(elem, str):
            text = elem

        # Renderiza texto
        txt_surf = font.render(text, True, color)
        surface.blit(txt_surf, (x, y))
        x += txt_surf.get_width() + 5  # espaçamento pequeno
        max_height = max(max_height, txt_surf.get_height())

    return max_height
