import math
import random
from typing import List, Optional, Sequence, Tuple, TypedDict
import pygame
from config.settings import Settings
from rendering.sprite_renderer import SpriteRenderer
from entities.colony import Colony
from entities.ant import Ant


Vec2 = Tuple[int, int]


class MovingAnt(TypedDict):
    position: pygame.Vector2
    destination: pygame.Vector2
    origin_index: int
    dest_index: int
    angle: float
    ant_obj: Ant


class GameEngine:
    def __init__(self, screen: pygame.Surface, settings: Settings) -> None:
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.settings: Settings = settings
        self.screen: pygame.Surface = screen
        self.running: bool = True
        self.sprites: SpriteRenderer = SpriteRenderer(settings)
        self.font: pygame.font.Font = pygame.font.SysFont(None, self.settings.FONT_SIZE)

        # Carrega posições dos ninhos a partir de Settings (fácil configuração)
        configured_positions = getattr(self.settings, "NEST_POSITIONS", [(200, 200), (600, 200)])
        # Garante tuplas e tipagem estrita
        self.nest_positions: List[Vec2] = [tuple(pos) for pos in configured_positions]

        # Embaralha a ordem dos ninhos se configurado
        if getattr(self.settings, "RANDOMIZE_NEST_POSITIONS", False):
            random.shuffle(self.nest_positions)

        # Prepara rects para interação/renderização
        self.nest_rects: List[pygame.Rect] = []
        if self.sprites.nest_img:
            for pos in self.nest_positions:
                self.nest_rects.append(self.sprites.nest_img.get_rect(center=pos))
        else:
            w, h = self.settings.NEST_SIZE
            half_w, half_h = w // 2, h // 2
            for pos in self.nest_positions:
                self.nest_rects.append(pygame.Rect(pos[0] - half_w, pos[1] - half_h, w, h))

        # Inicializa colônias (usa objetos Colony em vez de contadores simples)
        self.colonies: List[Colony] = [Colony(pos) for pos in self.nest_positions]

        # Preenche as colônias com formigas iniciais conforme Settings
        initial_counts = getattr(self.settings, "INITIAL_ANTS_PER_NEST", [1] * len(self.nest_positions))
        if isinstance(initial_counts, list) and len(initial_counts) >= len(self.colonies):
            counts = initial_counts[: len(self.colonies)]
        elif isinstance(initial_counts, list) and len(initial_counts) > 0:
            counts = [initial_counts[0]] * len(self.colonies)
        elif isinstance(initial_counts, int):
            counts = [initial_counts] * len(self.colonies)
        else:
            counts = [0] * len(self.colonies)

        for colony, c in zip(self.colonies, counts):
            colony.spawn_ants(c)

        self.selected_nest_index: Optional[int] = None
        # Lista de formigas em movimento (permite múltiplos movimentos simultâneos)
        # Cada item contém também o objeto `Ant` removido da colônia de origem.
        self.moving_ants: List[MovingAnt] = []
        self.frame_index: int = 0
        self.last_frame_toggle_ms: int = 0

    def _calculate_rotation_angle(self, origin: Sequence[float], destination: Sequence[float]) -> float:
        dx = destination[0] - origin[0]
        dy = destination[1] - origin[1]
        if dx == 0 and dy == 0:
            return 0.0
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad) + 90.0
        return angle_deg

    def _start_ant_movement(self, origin_index: int, dest_index: int) -> None:
        # Inicia movimento de uma formiga do ninho de origem para o destino
        if origin_index < 0 or origin_index >= len(self.nest_positions):
            return
        if dest_index < 0 or dest_index >= len(self.nest_positions):
            return

        # Verifica se há formigas no ninho de origem e remove uma para movimentar
        if origin_index < 0 or origin_index >= len(self.colonies):
            return
        if dest_index < 0 or dest_index >= len(self.colonies):
            return

        origin_colony = self.colonies[origin_index]
        ant_obj = origin_colony.remove_ant()
        if ant_obj is None:
            return

        origin = self.nest_positions[origin_index]
        dest = self.nest_positions[dest_index]
        angle = self._calculate_rotation_angle(origin, dest)

        # Cria registro de formiga em movimento mantendo referência ao objeto
        ant: MovingAnt = {
            "position": pygame.Vector2(origin),
            "destination": pygame.Vector2(dest),
            "origin_index": origin_index,
            "dest_index": dest_index,
            "angle": angle,
            "ant_obj": ant_obj,
        }
        self.moving_ants.append(ant)

    def _update_sprite_animation(self) -> None:
        now = pygame.time.get_ticks()
        # Alterna frame apenas se houver formigas em movimento
        if not self.moving_ants:
            return
        if now - self.last_frame_toggle_ms >= self.settings.ANIM_INTERVAL_MS:
            self.frame_index = 1 - self.frame_index
            self.last_frame_toggle_ms = now

    def _update_ant_movement(self) -> None:
        # Atualiza todas as formigas em movimento
        if not self.moving_ants:
            return

        # Itera sobre cópia da lista para permitir remoção segura
        for ant in list(self.moving_ants):
            direction: pygame.Vector2 = ant["destination"] - ant["position"]
            distance = direction.length()
            if distance <= self.settings.SPEED:
                ant["position"].update(ant["destination"])  # encaixa na posição de destino
                dest_index = ant.get("dest_index", None)
                # Adiciona o objeto Ant à colônia de destino
                if dest_index is not None and 0 <= dest_index < len(self.colonies):
                    ant_obj = ant.get("ant_obj", None)
                    if isinstance(ant_obj, Ant):
                        self.colonies[dest_index].ants.append(ant_obj)
                # Remove a formiga da lista de movimentos
                try:
                    self.moving_ants.remove(ant)
                except ValueError:
                    pass
                continue
            direction.scale_to_length(self.settings.SPEED)
            ant["position"] += direction

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_click(event.pos)

    def _handle_mouse_click(self, mouse_pos: Tuple[int, int]) -> None:
        # Permite iniciar múltiplos movimentos; não bloqueia caso já haja formigas movendo-se
        for index, rect in enumerate(self.nest_rects):
            if rect.collidepoint(mouse_pos):
                if self.selected_nest_index is None:
                    # Seleciona apenas se houver formigas disponíveis no ninho
                    available = len(self.colonies[index].ants)
                    if available > 0:
                        self.selected_nest_index = index
                else:
                    if index != self.selected_nest_index:
                        self._start_ant_movement(self.selected_nest_index, index)
                    self.selected_nest_index = None
                break

    def _render_ant_count(self, index: int, rect: pygame.Rect) -> None:
        # Contagem = formigas estacionadas na colônia + formigas que estão vindo para cá
        base = len(self.colonies[index].ants)
        incoming = sum(1 for a in self.moving_ants if a.get("dest_index") == index)
        count = base + incoming
        img = self.font.render(str(count), True, self.settings.TEXT_COLOR)
        self.screen.blit(img, (rect.centerx - 5, rect.bottom + 5))

    def _render(self) -> None:
        self.screen.fill(self.settings.BG_COLOR)
        # Desenha ninhos
        for i, pos in enumerate(self.nest_positions):
            self.sprites.draw_nest(self.screen, pos)
            # círculo de seleção
            if self.selected_nest_index == i:
                pygame.draw.circle(
                    self.screen,
                    self.settings.SELECTION_COLOR,
                    pos,
                    self.settings.NEST_SIZE[0] // 2 + 5,
                    3,
                )
            # contagem abaixo
            rect = self.nest_rects[i]
            self._render_ant_count(i, rect)
            
        # Desenha todas as formigas em movimento
        for ant in self.moving_ants:
            self.sprites.draw_ant(
                self.screen,
                ant["position"],
                ant["angle"],
                self.frame_index,
            )

        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            self._handle_events()
            if self.moving_ants:
                self._update_sprite_animation()
            self._update_ant_movement()
            self._render()
            self.clock.tick(self.settings.FPS)
