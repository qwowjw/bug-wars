"""
Cena de Derrota.
Exibida quando o jogador perde a fase.
"""

import pygame
from typing import Any, Optional
from src.core.engine import IScene
from src.core.events import Event, MouseButtonDown
from src.config.settings import Settings


class DefeatScene(IScene):
    """Cena exibida após derrota em uma fase."""

    def __init__(self) -> None:
        self.running = True
        self._next_event: Optional[Event] = None

        # Fonts
        self.font_title = pygame.font.SysFont("arial", 60, bold=True)
        self.font_text = pygame.font.SysFont("arial", 28)
        self.font_button = pygame.font.SysFont("arial", 24)

        # Botões
        self.btn_retry = pygame.Rect(0, 0, 200, 60)
        self.btn_menu = pygame.Rect(0, 0, 200, 60)

        # Layout: 2 botões em linha horizontal
        button_y = Settings.HEIGHT - 100
        self.btn_retry.midtop = (Settings.WIDTH // 2 - 150, button_y)
        self.btn_menu.midtop = (Settings.WIDTH // 2 + 150, button_y)

    def handle_event(self, event: Any) -> None:
        if isinstance(event, MouseButtonDown) and event.button == 1:
            if self.btn_retry.collidepoint(event.pos):
                from src.core.events import RetryLevelEvent
                self._next_event = RetryLevelEvent()
                self.running = False

            elif self.btn_menu.collidepoint(event.pos):
                from src.core.events import GameStartEvent
                self._next_event = GameStartEvent()
                self.running = False

    def update(self, dt: float) -> None:
        """Nada a fazer no update para cena estática."""
        pass

    def _draw_button(
        self, surface: pygame.Surface, rect: pygame.Rect, text: str
    ) -> None:
        """Desenha um botão com efeito de hover."""
        mouse_pos = pygame.mouse.get_pos()
        color = (200, 50, 50) if rect.collidepoint(mouse_pos) else (150, 30, 30)

        pygame.draw.rect(surface, color, rect, border_radius=10)
        pygame.draw.rect(surface, (255, 255, 255), rect, 2, border_radius=10)

        txt = self.font_button.render(text, True, (255, 255, 255))
        surface.blit(txt, txt.get_rect(center=rect.center))

    def render(self, surface: Any) -> None:
        """Renderiza a cena de derrota."""
        surface.fill(Settings.BG_COLOR)

        # Título
        title = self.font_title.render("DERROTA!", True, (255, 0, 0))
        surface.blit(title, title.get_rect(center=(Settings.WIDTH // 2, 100)))

        # Mensagem
        msg = self.font_text.render(
            "Você perdeu a fase. Tente novamente!", True, (200, 100, 100)
        )
        surface.blit(msg, msg.get_rect(center=(Settings.WIDTH // 2, 220)))

        # Botões
        self._draw_button(surface, self.btn_retry, "REPETIR")
        self._draw_button(surface, self.btn_menu, "MENU")

    @property
    def result_event(self) -> Optional[Event]:
        return self._next_event
