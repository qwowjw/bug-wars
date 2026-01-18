"""
Cena de Vitória.
Exibe o resultado da fase (score, tempo, estrelas) e oferece opções de navegação.
"""

import pygame
from typing import Any, Optional
from src.core.engine import IScene
from src.core.events import Event, MouseButtonDown
from src.core.events import LevelResult
from src.config.settings import Settings
from src.utils.asset_loader import load_image
from typing import List, Tuple


class VictoryScene(IScene):
    """Cena exibida após vitória em uma fase."""

    def __init__(self, result: LevelResult) -> None:
        self.result = result
        self.running = True
        self._next_event: Optional[Event] = None

        self.img_star_yellow: Optional[pygame.Surface] = load_image(Settings.IMG_STAR_YELLOW)
        self.img_star_black: Optional[pygame.Surface] = load_image(Settings.IMG_STAR_BLACK)

        # Redimensiona as imagens das estrelas
        star_size = (64, 64)
        if self.img_star_yellow:
            self.img_star_yellow = pygame.transform.smoothscale(self.img_star_yellow, star_size)
        if self.img_star_black:
            self.img_star_black = pygame.transform.smoothscale(self.img_star_black, star_size)

        # Fonts
        self.font_title = pygame.font.SysFont("arial", 60, bold=True)
        self.font_subtitle = pygame.font.SysFont("arial", 36, bold=True)
        self.font_text = pygame.font.SysFont("arial", 28)
        self.font_button = pygame.font.SysFont("arial", 24)

        # Botões
        self.btn_next = pygame.Rect(0, 0, 200, 60)
        self.btn_retry = pygame.Rect(0, 0, 200, 60)
        self.btn_menu = pygame.Rect(0, 0, 200, 60)

        # Layout: 3 botões em linha horizontal
        button_y = Settings.HEIGHT - 100
        self.btn_next.midtop = (Settings.WIDTH // 2 - 220, button_y)
        self.btn_retry.midtop = (Settings.WIDTH // 2, button_y)
        self.btn_menu.midtop = (Settings.WIDTH // 2 + 220, button_y)

    def handle_event(self, event: Any) -> None:
        if isinstance(event, MouseButtonDown) and event.button == 1:
            if self.btn_next.collidepoint(event.pos):
                from src.core.events import NextLevelEvent
                self._next_event = NextLevelEvent()
                self.running = False

            elif self.btn_retry.collidepoint(event.pos):
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

    def _draw_stars(self, surface: pygame.Surface, center_x: int, base_y: int) -> None:
        """
        Desenha as estrelas usando imagens PNG.
        Layout: Esquerda, Centro (mais alta), Direita.
        """
        # Configuração de posicionamento
        spacing_x = 70       # Distância horizontal entre as estrelas
        elevation_y = 30     # Quanto a estrela do meio sobe em relação às outras

        # Define as posições (x, y) para as 3 estrelas
        # Índice 0: Esquerda
        # Índice 1: Centro (Elevada - Y menor)
        # Índice 2: Direita
        positions: List[Tuple[int, int]] = [
            (center_x - spacing_x, base_y),             # Esquerda
            (center_x, base_y - elevation_y),           # Centro (Topo)
            (center_x + spacing_x, base_y)              # Direita
        ]

        for i, pos in enumerate(positions):
            # Lógica de preenchimento:
            # Se o jogador tem X estrelas, as primeiras X posições são amarelas (yellow),
            # o restante é preto (black).
            # Ex: 2 estrelas -> indices 0 e 1 (Yellow), indice 2 (Black).
            is_earned = i < self.result.stars
            
            img = self.img_star_yellow if is_earned else self.img_star_black

            if img:
                # Centraliza a imagem na coordenada calculada
                rect = img.get_rect(center=pos)
                surface.blit(img, rect)
            else:
                # Fallback caso a imagem não carregue (círculo colorido)
                color = (255, 215, 0) if is_earned else (50, 50, 50)
                pygame.draw.circle(surface, color, pos, 20)
                pygame.draw.circle(surface, (255, 255, 255), pos, 20, 2)
    def _draw_button(
        self, surface: pygame.Surface, rect: pygame.Rect, text: str
    ) -> None:
        """Desenha um botão com efeito de hover."""
        mouse_pos = pygame.mouse.get_pos()
        color = (50, 200, 50) if rect.collidepoint(mouse_pos) else (30, 150, 30)

        pygame.draw.rect(surface, color, rect, border_radius=10)
        pygame.draw.rect(surface, (255, 255, 255), rect, 2, border_radius=10)

        txt = self.font_button.render(text, True, (255, 255, 255))
        surface.blit(txt, txt.get_rect(center=rect.center))

    def render(self, surface: Any) -> None:
        """Renderiza a cena de vitória."""
        surface.fill(Settings.BG_COLOR)

        # Calculamos o centro horizontal e alturas relativas
        cx = Settings.WIDTH // 2
        h = Settings.HEIGHT

        # Título
        title = self.font_title.render("VITÓRIA!", True, (0, 255, 0))
        surface.blit(title, title.get_rect(center=(cx, int(h * 0.15))))

        # Estrelas
        self._draw_stars(surface, center_x=cx, base_y=int(h * 0.30))

        # Score
        score_text = self.font_subtitle.render(
            f"Score: {self.result.score}", True, (255, 255, 255)
        )
        surface.blit(score_text, score_text.get_rect(center=(cx, int(h * 0.50))))

        # Tempo
        time_text = self.font_text.render(
            f"Tempo: {self.result.time_spent:.1f}s", True, (200, 200, 200)
        )
        surface.blit(time_text, time_text.get_rect(center=(cx, int(h * 0.60))))

        # Estrelas obtidas
        stars_info = self.font_text.render(
            f"({self.result.stars}/3)", True, (100, 100, 100)
        )
        surface.blit(stars_info, stars_info.get_rect(center=(cx, int(h * 0.68))))

        # Botões
        button_y = int(h * 0.85)
        self.btn_next.midtop = (cx - 220, button_y)
        self.btn_retry.midtop = (cx, button_y)
        self.btn_menu.midtop = (cx + 220, button_y)

        self._draw_button(surface, self.btn_next, "PRÓXIMA")
        self._draw_button(surface, self.btn_retry, "REPETIR")
        self._draw_button(surface, self.btn_menu, "MENU")

    @property
    def result_event(self) -> Optional[Event]:
        return self._next_event
