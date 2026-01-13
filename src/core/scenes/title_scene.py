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
        self._start_requested = False

        # Configuração do Botão
        self.btn_rect = pygame.Rect(0, 0, 200, 60)
        self.btn_rect.center = (Settings.WIDTH // 2, Settings.HEIGHT // 2 + 50)

    def handle_event(self, event: Any) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clique esquerdo
                if self.btn_rect.collidepoint(event.pos):
                    self._start_requested = True
                    self.running = False  # Encerra esta cena para o engine trocar

    def update(self, dt: float) -> None:
        # Animações de fundo poderiam vir aqui
        pass

    def render(self, surface: Any) -> None:
        """
        Renderiza a cena de título.
        
        Args:
            surface: A superfície do Pygame onde a cena será desenhada.
        """
        # A assinatura foi corrigida para remover 'events', alinhando com o PygameAdapter
        
        surface.fill(Settings.BG_COLOR)

        # Título
        title_surf = self.font_title.render("Ant Simulator", True, Settings.SELECTION_COLOR)
        title_rect = title_surf.get_rect(center=(Settings.WIDTH // 2, Settings.HEIGHT // 3))
        surface.blit(title_surf, title_rect)

        # Botão Tutorial
        mouse_pos = pygame.mouse.get_pos()
        # Highlight se o mouse estiver sobre o botão
        btn_color = (50, 200, 50) if self.btn_rect.collidepoint(mouse_pos) else (30, 150, 30)
        
        pygame.draw.rect(surface, btn_color, self.btn_rect, border_radius=10)
        pygame.draw.rect(surface, (255, 255, 255), self.btn_rect, 2, border_radius=10)
        
        txt_surf = self.font_btn.render("TUTORIAL", True, (255, 255, 255))
        txt_rect = txt_surf.get_rect(center=self.btn_rect.center)
        surface.blit(txt_surf, txt_rect)

    @property
    def next_action(self) -> Event:
        """Helper para o Main saber o que fazer quando a cena acabar."""
        if self._start_requested:
            return GameStartEvent()
        return Event()  # Evento vazio padrão