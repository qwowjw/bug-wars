import math
import random
from typing import List, Optional, Sequence, Tuple, TypedDict, Union
import pygame
from config.settings import Settings
from rendering.sprite_renderer import SpriteRenderer
from entities.colony import Colony
from entities.ant_types import ANT_TYPES_BY_NAME, farao
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
        nest_img = getattr(self.sprites, "nest_img", None)
        if nest_img:
            for pos in self.nest_positions:
                self.nest_rects.append(nest_img.get_rect(center=pos))
        else:
            w, h = self.settings.NEST_SIZE
            half_w, half_h = w // 2, h // 2
            for pos in self.nest_positions:
                self.nest_rects.append(pygame.Rect(pos[0] - half_w, pos[1] - half_h, w, h))

        # Inicializa colônias (usa objetos Colony em vez de contadores simples)
        # Usa tipos configuráveis via Settings: INITIAL_ANT_TYPE_PER_NEST ou DEFAULT_ANT_TYPE_NAME
        type_names = getattr(self.settings, "INITIAL_ANT_TYPE_PER_NEST", None)
        default_name = getattr(self.settings, "DEFAULT_ANT_TYPE_NAME", "Farao")
        self.colonies: List[Colony] = []
        for idx, pos in enumerate(self.nest_positions):
            name = None
            if isinstance(type_names, list) and idx < len(type_names):
                name = type_names[idx]
            if not name:
                name = default_name
            ant_type = ANT_TYPES_BY_NAME.get(name, farao)
            self.colonies.append(Colony(pos, ant_type=ant_type))

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
        # Fila de transferências pendentes para envio sequencial (origin, dest, remaining)
        self.pending_transfers: List[dict] = []
        self.frame_index: int = 0
        self.last_frame_toggle_ms: int = 0

    def _calculate_rotation_angle(self, origin: Union[Sequence[float], pygame.Vector2], destination: Union[Sequence[float], pygame.Vector2]) -> float:
        dx = destination[0] - origin[0]
        dy = destination[1] - origin[1]
        if dx == 0 and dy == 0:
            return 0.0
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad) + 90.0
        return angle_deg

    def _ant_rect_from_pos(self, pos: pygame.Vector2) -> pygame.Rect:
        w, h = self.settings.ANT_SIZE
        return pygame.Rect(int(pos.x - w // 2), int(pos.y - h // 2), w, h)

    def _start_ant_movement(self, origin_index: int, dest_index: int, offset_index: int = 0) -> None:
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

        origin = pygame.Vector2(self.nest_positions[origin_index])
        dest = pygame.Vector2(self.nest_positions[dest_index])
        angle = self._calculate_rotation_angle(origin, dest)

        # Calcula pequeno deslocamento ao longo da direção para criar uma fila
        direction = dest - origin
        if direction.length() != 0:
            dir_norm = direction.normalize()
        else:
            # Se origem==dest, usa deslocamento horizontal para separar sprites
            dir_norm = pygame.Vector2(1, 0)

        # Espaçamento entre formigas em pixels (configurável via Settings)
        default_spacing = max(8, min(self.settings.ANT_SIZE) // 3)
        spacing = getattr(self.settings, "ANT_SPACING_PX", default_spacing)

        # Tenta encontrar um offset que não colida com outras formigas em movimento
        attempt = 0
        max_attempts = 12
        candidate_offset = offset_index
        candidate_pos = origin - dir_norm * spacing * candidate_offset
        candidate_rect = self._ant_rect_from_pos(candidate_pos)

        existing_rects = [self._ant_rect_from_pos(a["position"]) for a in self.moving_ants]
        while any(candidate_rect.colliderect(r) for r in existing_rects) and attempt < max_attempts:
            attempt += 1
            candidate_offset += 1
            candidate_pos = origin - dir_norm * spacing * candidate_offset
            candidate_rect = self._ant_rect_from_pos(candidate_pos)

        # Cria registro de formiga em movimento mantendo referência ao objeto
        ant: MovingAnt = {
            "position": pygame.Vector2(candidate_pos),
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

            dest_index = ant.get("dest_index", None)
            arrived = False

            # Verifica colisão do rect da formiga com o rect do ninho destino
            if dest_index is not None and 0 <= dest_index < len(self.nest_rects):
                ant_rect = self._ant_rect_from_pos(ant["position"])
                dest_rect = self.nest_rects[dest_index]
                if ant_rect.colliderect(dest_rect):
                    arrived = True

            if arrived:
                # Coloca a formiga na colônia destino
                if dest_index is not None and 0 <= dest_index < len(self.colonies):
                    ant_obj = ant.get("ant_obj", None)
                    if isinstance(ant_obj, Ant):
                        self.colonies[dest_index].ants.append(ant_obj)
                try:
                    self.moving_ants.remove(ant)
                except ValueError:
                    pass
                # Render imediato para refletir a atualização da contagem
                try:
                    self._render()
                except Exception:
                    pass
                continue

            # Move a formiga na direção do destino
            if direction.length() == 0:
                # Sem direção (já na posição): apenas continue para a próxima
                continue
            direction.scale_to_length(self.settings.SPEED)
            ant["position"] += direction


    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Passa o evento para detectar modificadores (Shift)
                self._handle_mouse_click(event)

    def _handle_mouse_click(self, event) -> None:
        mouse_pos: Tuple[int, int] = event.pos
        mods = pygame.key.get_mods()
        shift_pressed = bool(mods & pygame.KMOD_SHIFT)

        for index, rect in enumerate(self.nest_rects):
            if rect.collidepoint(mouse_pos):
                # CASO 1: Cancelar envios se clicar no ninho que já estava selecionado
                if self.selected_nest_index == index:
                    # Remove todas as transferências que têm este ninho como origem
                    self.pending_transfers = [t for t in self.pending_transfers if t["origin"] != index]
                    self.selected_nest_index = None
                    return

                # CASO 2: Selecionar origem
                if self.selected_nest_index is None:
                    if len(self.colonies[index].ants) > 0:
                        self.selected_nest_index = index
                
                # CASO 3: Definir destino
                else:
                    origin_idx = self.selected_nest_index
                    origin_colony = self.colonies[origin_idx]
                    
                    if shift_pressed:
                        self._start_ant_movement(origin_idx, index)
                    else:
                        available = len(origin_colony.ants)
                        if available > 0:
                            # Adiciona nova transferência sem bloquear as existentes
                            self.pending_transfers.append({
                                "origin": origin_idx, 
                                "dest": index, 
                                "remaining": available
                            })
                    
                    # Limpa seleção para permitir selecionar outra origem ou o mesmo novamente
                    self.selected_nest_index = None
                break

    def _process_pending_transfers(self) -> None:
        """Processa transferências pendentes permitindo envios simultâneos para destinos diferentes.
        
        Notes:
            Itera por todas as transferências pendentes e verifica se há espaço
            na direção específica de cada destino. Isso permite que um mesmo
            formigueiro envie formigas simultaneamente para múltiplos destinos.
        """
        if not self.pending_transfers:
            return

        spacing: int = max(8, min(self.settings.ANT_SIZE) // 3)

        for transfer in list(self.pending_transfers):
            origin_idx: int = transfer["origin"]
            dest_idx: int = transfer["dest"]

            # Validação de segurança
            if origin_idx >= len(self.colonies) or not self.colonies[origin_idx].ants:
                self.pending_transfers.remove(transfer)
                continue

            # Calcula posição inicial da formiga na direção do destino específico
            origin_pos: pygame.Vector2 = pygame.Vector2(self.nest_positions[origin_idx])
            dest_pos: pygame.Vector2 = pygame.Vector2(self.nest_positions[dest_idx])
            direction: pygame.Vector2 = dest_pos - origin_pos
            dir_norm: pygame.Vector2 = direction.normalize() if direction.length() != 0 else pygame.Vector2(1, 0)
            
            # Posição inicial deslocada na direção do destino
            spawn_offset: int = spacing * 2
            candidate_pos: pygame.Vector2 = origin_pos + dir_norm * spawn_offset
            candidate_rect: pygame.Rect = self._ant_rect_from_pos(candidate_pos)

            # Verifica colisão apenas com formigas já em movimento
            existing_rects: List[pygame.Rect] = [self._ant_rect_from_pos(a["position"]) for a in self.moving_ants]
            
            # Se não houver colisão nesta direção específica, despacha a formiga
            if not any(candidate_rect.colliderect(r) for r in existing_rects):
                self._start_ant_movement(origin_idx, dest_idx, 0)
                transfer["remaining"] -= 1
                
                if transfer["remaining"] <= 0:
                    self.pending_transfers.remove(transfer)


    def _render_ant_count(self, index: int, rect: pygame.Rect) -> None:
        """Renderiza a contagem de formigas no ninho.
        
        Args:
            index: Índice do ninho na lista de colônias.
            rect: Retângulo do ninho para posicionamento do texto.
        
        Notes:
            Mostra apenas as formigas que já estão fisicamente no ninho,
            sem contar as que estão em trânsito.
        """
        count = len(self.colonies[index].ants)
        img = self.font.render(str(count), True, self.settings.TEXT_COLOR)
        self.screen.blit(img, (rect.centerx - 5, rect.bottom + 5))

    def _render(self) -> None:
        self.screen.fill(self.settings.BG_COLOR)
        # Desenha ninhos
        for i, pos in enumerate(self.nest_positions):
            # determine nest image state: allied if colony has any ants, empty if zero
            state = "ally" if len(self.colonies[i].ants) > 0 else "empty"
            self.sprites.draw_nest(self.screen, pos, state=state)
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
            # Tenta processar uma transferência pendente (uma formiga por ciclo)
            self._process_pending_transfers()
            # Atualiza produção das colônias (delta em segundos)
            dt = self.clock.get_time() / 1000.0
            for colony in self.colonies:
                produced = colony.update(dt)
                if produced > 0:
                    # re-render para refletir nova contagem imediatamente
                    try:
                        self._render()
                    except Exception:
                        pass
            if self.moving_ants:
                self._update_sprite_animation()
            self._update_ant_movement()
            self._render()
            self.clock.tick(self.settings.FPS)
