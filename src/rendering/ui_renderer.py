import pygame
from src.config.settings import Settings


class UIRenderer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.font = pygame.font.SysFont("consolas", 18)

    def draw_hud(
        self, surface: pygame.Surface, ant_count: int, nest_count: int
    ) -> None:
        text = f"Ants: {ant_count} | Nests: {nest_count}"
        img = self.font.render(text, True, self.settings.UI_COLOR)
        surface.blit(img, (10, 10))
