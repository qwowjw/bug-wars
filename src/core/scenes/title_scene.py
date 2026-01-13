import pygame
from typing import Any
from core.engine import IScene
from core.events import Event, GameStartEvent
from config.settings import Settings


class TitleScene(IScene):
    """
    Cena de Título (Menu Principal).
    Gerencia a exibição da tela inicial, o botão de tutorial e o botão de jogar.
    """

    def __init__(self, screen_surface: pygame.Surface) -> None:
        self.screen = screen_surface
        self.running = True
        self.font_title = pygame.font.SysFont("arial", 60, bold=True)
        self.font_btn = pygame.font.SysFont("arial", 40)

        self._next_event: Event | None = None

        self.btn_tutorial = pygame.Rect(0, 0, 240, 60)
        self.btn_play = pygame.Rect(0, 0, 240, 60)

        self.btn_tutorial.center = (Settings.WIDTH // 2, Settings.HEIGHT // 2 + 30)
        self.btn_play.center = (Settings.WIDTH // 2, Settings.HEIGHT // 2 + 110)

    def handle_event(self, event: Any) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_tutorial.collidepoint(event.pos):
                self._next_event = GameStartEvent()
                self.running = False

            elif self.btn_play.collidepoint(event.pos):
                from core.events import CampaignStartEvent

                self._next_event = CampaignStartEvent()
                self.running = False

    def update(self, dt: float) -> None:
        # Animações de fundo poderiam vir aqui
        pass

    def _draw_button(self, surface, rect, text):
        mouse_pos = pygame.mouse.get_pos()
        color = (50, 200, 50) if rect.collidepoint(mouse_pos) else (30, 150, 30)

        pygame.draw.rect(surface, color, rect, border_radius=10)
        pygame.draw.rect(surface, (255, 255, 255), rect, 2, border_radius=10)

        txt = self.font_btn.render(text, True, (255, 255, 255))
        surface.blit(txt, txt.get_rect(center=rect.center))

    def render(self, surface: Any) -> None:
        """
        Renderiza a cena de título.

        Args:
            surface: A superfície do Pygame onde a cena será desenhada.
        """

        surface.fill(Settings.BG_COLOR)

        title = self.font_title.render("Ant Simulator", True, Settings.SELECTION_COLOR)
        surface.blit(
            title, title.get_rect(center=(Settings.WIDTH // 2, Settings.HEIGHT // 3))
        )

        self._draw_button(surface, self.btn_tutorial, "TUTORIAL")
        self._draw_button(surface, self.btn_play, "JOGAR")

    @property
    def next_action(self) -> Event:
        """Helper para o Main saber o que fazer quando a cena acabar."""
        return self._next_event or Event()
