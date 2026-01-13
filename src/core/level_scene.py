from __future__ import annotations

import logging
from typing import (
    Any,
    List,
    Optional,
    Sequence,
    Tuple,
    TypedDict,
    Union,
    Literal,
    cast,
)
import math
import random
import concurrent.futures
from core.level_config import LevelConfig
from rendering.ui_helper import render_rich_text_line
from core.events import Event, LevelCompleteEvent
from ai.enemy_controller import (
    EnemyController,
    AI_BALANCED,
)

import pygame

from config.settings import Settings
from rendering.sprite_renderer import SpriteRenderer
from entities.colony import Colony
from entities.ant_types import ANT_TYPES_BY_NAME, farao
from entities.ant import Ant


Vec2 = Tuple[int, int]
Owner = Literal["ally", "enemy", "empty"]


class MovingAnt(TypedDict):
    position: pygame.Vector2
    destination: pygame.Vector2
    origin_index: int
    dest_index: int
    angle: float
    ant_obj: Ant
    owner: Owner


def default_victory_condition(owners: List[Owner], colonies: List[Colony]) -> bool:
    return all(o == "ally" for o in owners)


# Level presets moved to src/core/levels.py


class LevelScene:
    """Scene that runs one level using ECS-like separation of concerns.

    Systems responsibilities (logical grouping):
      - InputSystem: selection and transfer intents.
      - TransferSystem: queueing and spawning moving ants safely.
      - MovementSystem: move ants and resolve arrivals.
      - ProductionSystem: update colonies (parallelized where safe).
      - RenderSystem: draw nests, counts, moving ants.

    Keep the main loop simple and low-allocation; avoid creating objects in hot paths.
    """

    def __init__(
        self, screen: pygame.Surface, settings: Settings, config: LevelConfig
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.settings: Settings = settings
        self.screen: pygame.Surface = screen
        self.running: bool = True
        self.sprites: SpriteRenderer = SpriteRenderer(settings)
        self.font: pygame.font.Font = pygame.font.SysFont(None, self.settings.FONT_SIZE)
        config.validate()
        self.config: LevelConfig = config

        # Setup nest positions
        self.nest_positions: List[Vec2] = [
            cast(Vec2, tuple(p)) for p in self.config.nest_positions
        ]
        if self.config.randomize_positions:
            random.shuffle(self.nest_positions)

        # Build rects for input/render alignment
        self.nest_rects: List[pygame.Rect] = []
        nest_img = getattr(self.sprites, "nest_img_ally", None) or getattr(
            self.sprites, "nest_img_empty", None
        )
        if nest_img:
            for pos in self.nest_positions:
                self.nest_rects.append(nest_img.get_rect(center=pos))
        else:
            w, h = self.settings.NEST_SIZE
            half_w, half_h = w // 2, h // 2
            for pos in self.nest_positions:
                self.nest_rects.append(
                    pygame.Rect(pos[0] - half_w, pos[1] - half_h, w, h)
                )

        # Owners and colonies
        self.owners: List[Owner] = list(self.config.initial_owners)
        self.colonies: List[Colony] = []
        type_names = self.config.ant_types or [
            self.settings.DEFAULT_ANT_TYPE_NAME
        ] * len(self.nest_positions)

        for idx, pos in enumerate(self.nest_positions):
            name = (
                type_names[idx]
                if idx < len(type_names)
                else self.settings.DEFAULT_ANT_TYPE_NAME
            )
            ant_type = ANT_TYPES_BY_NAME.get(name, farao)
            colony = Colony(pos, ant_type=ant_type)
            self.colonies.append(colony)

        # Spawn initial ants based on counts and owners
        for i, c in enumerate(self.config.initial_counts):
            if self.owners[i] != "empty" and c > 0:
                self.colonies[i].spawn_ants(int(c))

        # Selection and movement state
        # Support multi-selection of ally nests
        self.selected_nest_indices: set[int] = set()
        self.moving_ants: List[MovingAnt] = []
        self.pending_transfers: List[dict] = []  # {origin, dest, remaining}
        self.frame_index: int = 0
        self.last_frame_toggle_ms: int = 0

        # Thread pool for production system
        workers = max(1, int(getattr(self.settings, "THREAD_WORKERS", 0)) or 0)
        # Keep lazy-creation: build an executor only if workers > 1
        self._thread_workers = workers

        self.logger.info(
            "Level '%s' initialized with %d nests",
            self.config.name,
            len(self.nest_positions),
        )

        # Estado do jogo
        self.state: str = (
            "tutorial" if getattr(self.config, "tutorial", None) else "playing"
        )

        self.tutorial_font = pygame.font.SysFont("arial", 24)
        self.completed: bool = False

        # --- Configuração da IA Inimiga ---
        profile = self.config.ai_profile or AI_BALANCED
        self.enemy_ai = EnemyController(self, profile)

        self.logger.info(f"Nível {config.name} iniciado. IA: {profile.name}")

    # -------------- Utility helpers --------------
    def _calculate_rotation_angle(
        self,
        origin: Union[Sequence[float], pygame.Vector2],
        destination: Union[Sequence[float], pygame.Vector2],
    ) -> float:
        dx = float(destination[0]) - float(origin[0])
        dy = float(destination[1]) - float(origin[1])
        if dx == 0.0 and dy == 0.0:
            return 0.0
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad) + 90.0
        return angle_deg

    def _ant_rect_from_pos(self, pos: pygame.Vector2) -> pygame.Rect:
        w, h = self.settings.ANT_SIZE
        return pygame.Rect(int(pos.x - w // 2), int(pos.y - h // 2), w, h)

    # -------------- Systems --------------
    # TransferSystem
    def _start_ant_movement(
        self, origin_index: int, dest_index: int, owner: Owner, offset_index: int = 0
    ) -> None:
        # Validate indices
        if origin_index < 0 or origin_index >= len(self.nest_positions):
            return
        if dest_index < 0 or dest_index >= len(self.nest_positions):
            return
        # allow movement for both ally and enemy (enemy AI will initiate transfers)
        if owner not in ("ally", "enemy"):
            return

        origin_colony = self.colonies[origin_index]
        ant_obj = origin_colony.remove_ant()
        if ant_obj is None:
            return
        # If removing the ant left the colony empty, mark ownership as empty
        if len(origin_colony.ants) == 0:
            self.owners[origin_index] = "empty"

        origin = pygame.Vector2(self.nest_positions[origin_index])
        dest = pygame.Vector2(self.nest_positions[dest_index])
        angle = self._calculate_rotation_angle(origin, dest)

        direction = dest - origin
        if direction.length() != 0:
            dir_norm = direction.normalize()
        else:
            dir_norm = pygame.Vector2(1, 0)

        default_spacing = max(8, min(self.settings.ANT_SIZE) // 3)
        spacing = int(getattr(self.settings, "ANT_SPACING_PX", default_spacing))

        attempt = 0
        max_attempts = 12
        candidate_offset = offset_index
        candidate_pos = origin - dir_norm * spacing * candidate_offset
        candidate_rect = self._ant_rect_from_pos(candidate_pos)

        existing_rects = [
            self._ant_rect_from_pos(a["position"]) for a in self.moving_ants
        ]
        while (
            any(candidate_rect.colliderect(r) for r in existing_rects)
            and attempt < max_attempts
        ):
            attempt += 1
            candidate_offset += 1
            candidate_pos = origin - dir_norm * spacing * candidate_offset
            candidate_rect = self._ant_rect_from_pos(candidate_pos)

        ant: MovingAnt = {
            "position": pygame.Vector2(candidate_pos),
            "destination": pygame.Vector2(dest),
            "origin_index": origin_index,
            "dest_index": dest_index,
            "angle": angle,
            "ant_obj": ant_obj,
            "owner": owner,
        }
        self.moving_ants.append(ant)
        self.logger.debug("Dispatched ant from %d to %d", origin_index, dest_index)

    def _process_pending_transfers(self) -> None:
        if not self.pending_transfers:
            return

        spacing: int = max(8, min(self.settings.ANT_SIZE) // 3)

        for transfer in list(self.pending_transfers):
            origin_idx: int = int(transfer["origin"])
            dest_idx: int = int(transfer["dest"])
            owner: Owner = self.owners[origin_idx]

            # process transfers for ally and enemy (enemy AI uses pending_transfers)
            if owner not in ("ally", "enemy"):
                self.pending_transfers.remove(transfer)
                continue

            if origin_idx >= len(self.colonies) or not self.colonies[origin_idx].ants:
                self.pending_transfers.remove(transfer)
                continue

            origin_pos: pygame.Vector2 = pygame.Vector2(self.nest_positions[origin_idx])
            dest_pos: pygame.Vector2 = pygame.Vector2(self.nest_positions[dest_idx])
            direction: pygame.Vector2 = dest_pos - origin_pos
            dir_norm: pygame.Vector2 = (
                direction.normalize()
                if direction.length() != 0
                else pygame.Vector2(1, 0)
            )

            spawn_offset: int = spacing * 2
            candidate_pos: pygame.Vector2 = origin_pos + dir_norm * spawn_offset
            candidate_rect: pygame.Rect = self._ant_rect_from_pos(candidate_pos)

            existing_rects: List[pygame.Rect] = [
                self._ant_rect_from_pos(a["position"]) for a in self.moving_ants
            ]

            if not any(candidate_rect.colliderect(r) for r in existing_rects):
                self._start_ant_movement(origin_idx, dest_idx, owner, 0)
                transfer["remaining"] -= 1
                if transfer["remaining"] <= 0:
                    self.pending_transfers.remove(transfer)

    # MovementSystem
    def _update_sprite_animation(self) -> None:
        now = pygame.time.get_ticks()
        if not self.moving_ants:
            return
        if now - self.last_frame_toggle_ms >= self.settings.ANIM_INTERVAL_MS:
            self.frame_index = 1 - self.frame_index
            self.last_frame_toggle_ms = now

    def _resolve_arrival(self, ant: MovingAnt) -> None:
        dest_index = int(ant["dest_index"])
        if dest_index < 0 or dest_index >= len(self.colonies):
            return
        dest_owner = self.owners[dest_index]
        dest_colony = self.colonies[dest_index]
        ant_owner = ant["owner"]

        if dest_owner == "empty":
            # Capture empty nest
            self.owners[dest_index] = ant_owner
            ant_obj = ant["ant_obj"]
            if isinstance(ant_obj, Ant):
                dest_colony.ants.append(ant_obj)
            self.logger.info("Nest %d captured by %s", dest_index, ant_owner)
            return

        if dest_owner == ant_owner:
            ant_obj = ant["ant_obj"]
            if isinstance(ant_obj, Ant):
                dest_colony.ants.append(ant_obj)
            return

        # Enemy destination: simple one-to-one reduction rule
        if dest_owner != ant_owner:
            if dest_colony.ants:
                dest_colony.ants.pop()  # remove one enemy ant
                # if defenders depleted, mark nest as empty
                if len(dest_colony.ants) == 0:
                    self.owners[dest_index] = "empty"
                self.logger.debug(
                    "Combat at nest %d: removed one enemy ant", dest_index
                )
                # arriving ant is consumed in the fight
                return
            else:
                # No defenders left — flip ownership and add arriving ant
                self.owners[dest_index] = ant_owner
                ant_obj = ant["ant_obj"]
                if isinstance(ant_obj, Ant):
                    dest_colony.ants.append(ant_obj)
                self.logger.info(
                    "Nest %d captured by %s after clearing defenders",
                    dest_index,
                    ant_owner,
                )
                return

    def _update_ant_movement(self) -> None:
        if not self.moving_ants:
            return
        for ant in list(self.moving_ants):
            direction: pygame.Vector2 = ant["destination"] - ant["position"]
            dest_index = int(ant.get("dest_index", -1))
            arrived = False

            if 0 <= dest_index < len(self.nest_rects):
                ant_rect = self._ant_rect_from_pos(ant["position"])  # current rect
                dest_rect = self.nest_rects[dest_index]
                if ant_rect.colliderect(dest_rect):
                    arrived = True

            if arrived:
                self._resolve_arrival(ant)
                try:
                    self.moving_ants.remove(ant)
                except ValueError:
                    pass
                continue

            if direction.length() == 0:
                continue
            direction.scale_to_length(self.settings.SPEED)
            ant["position"] += direction

    # ProductionSystem (parallelizable)
    def _update_production(self, dt: float) -> None:
        # Decide which colonies produce: allies always; enemy only if configured
        indices: List[int] = []
        for i, owner in enumerate(self.owners):
            if owner == "ally" or (owner == "enemy" and self.config.enemy_produces):
                indices.append(i)

        if not indices:
            return

        def _step(i: int) -> int:
            return self.colonies[i].update(dt)

        if self._thread_workers and self._thread_workers > 1:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=self._thread_workers
            ) as pool:
                results = list(pool.map(_step, indices))
        else:
            results = [_step(i) for i in indices]

        if any(p > 0 for p in results):
            # Re-render handled by main loop; logging here for visibility
            produced_total = sum(results)
            if produced_total:
                self.logger.debug(
                    "Produced %d ants across colonies this tick", produced_total
                )

    # -------------- Input handling --------------
    def handle_event(self, event: Any) -> None:
        if self.state == "tutorial":
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                self.state = "playing"
            return

        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_click(event)

    def _handle_mouse_click(self, event) -> None:
        mouse_pos: Tuple[int, int] = event.pos
        mods = pygame.key.get_mods()
        shift_pressed = bool(mods & pygame.KMOD_SHIFT)
        ctrl_pressed = bool(mods & (pygame.KMOD_CTRL | pygame.KMOD_META))

        for index, rect in enumerate(self.nest_rects):
            if not rect.collidepoint(mouse_pos):
                continue

            owner = self.owners[index]
            colony = self.colonies[index]

            # If clicking on an ally nest with ants: handle selection logic
            if owner == "ally" and len(colony.ants) > 0:
                if ctrl_pressed:
                    # Toggle selection with Ctrl (or Cmd)
                    if index in self.selected_nest_indices:
                        self.selected_nest_indices.remove(index)
                    else:
                        self.selected_nest_indices.add(index)
                    return
                else:
                    # Without Ctrl: replace selection with this single nest
                    self.selected_nest_indices = {index}
                    return

            # Otherwise, treat as destination if we have any selected origins
            if self.selected_nest_indices:
                # Shift on destination click still means: send one ant per selected origin
                for origin_idx in list(self.selected_nest_indices):
                    origin_owner = self.owners[origin_idx]
                    if origin_owner != "ally":
                        continue
                    origin_colony = self.colonies[origin_idx]
                    if shift_pressed:
                        # send a single ant immediately
                        self._start_ant_movement(origin_idx, index, origin_owner)
                    else:
                        available = len(origin_colony.ants)
                        if available > 0:
                            self.pending_transfers.append(
                                {
                                    "origin": origin_idx,
                                    "dest": index,
                                    "remaining": available,
                                }
                            )
                # Clear selection after issuing the command
                self.selected_nest_indices.clear()
                return

            # Nothing to do if clicked elsewhere without a valid selection
            return

    # -------------- Render --------------
    def _render_ant_count(self, index: int, rect: pygame.Rect) -> None:
        count = len(self.colonies[index].ants)
        img = self.font.render(str(count), True, self.settings.TEXT_COLOR)
        self.screen.blit(img, (rect.centerx - 5, rect.bottom + 5))

    def render(self, surface: Optional[pygame.Surface] = None) -> None:
        target = surface or self.screen
        target.fill(self.settings.BG_COLOR)

        # Nests
        for i, pos in enumerate(self.nest_positions):
            owner = self.owners[i]
            if owner == "ally":
                state = "ally"
            elif owner == "enemy":
                state = "enemy"
            else:
                state = "empty"
            self.sprites.draw_nest(target, pos, state=state)

            # selection ring (support multi-select)
            if i in self.selected_nest_indices:
                pygame.draw.circle(
                    target,
                    self.settings.SELECTION_COLOR,
                    pos,
                    self.settings.NEST_SIZE[0] // 2 + 5,
                    3,
                )

            # optional enemy ring overlay (red) if no enemy sprite available
            if owner == "enemy" and not getattr(self.sprites, "nest_img_enemy", None):
                pygame.draw.circle(
                    target,
                    (200, 60, 60),
                    pos,
                    self.settings.NEST_SIZE[0] // 2 + 2,
                    2,
                )

            rect = self.nest_rects[i]
            self._render_ant_count(i, rect)

        # Moving ants
        for ant in self.moving_ants:
            ant_obj = ant["ant_obj"]
            t_name = ant_obj.type.name if ant_obj else "Farao"
            self.sprites.draw_ant(
                target,
                ant["position"],
                ant["angle"],
                self.frame_index,
                ant_type_name=t_name,
            )

        if self.state == "tutorial" and getattr(self.config, "tutorial", None):
            self._render_tutorial_overlay(target)

        pygame.display.flip()

    def _render_tutorial_overlay(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface(
            (self.settings.WIDTH, self.settings.HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        tutorial = self.config.tutorial
        if not tutorial:
            return

        title_font = pygame.font.SysFont("arial", 40, bold=True)
        title_surf = title_font.render(tutorial.title, True, (255, 255, 0))
        title_rect = title_surf.get_rect(center=(self.settings.WIDTH // 2, 80))
        surface.blit(title_surf, title_rect)

        start_x = 100
        start_y = 150

        for line in tutorial.lines:
            h = render_rich_text_line(
                surface, line, (start_x, start_y), self.tutorial_font
            )
            start_y += h + 15

        cont_surf = self.tutorial_font.render(
            "Clique para iniciar...", True, (150, 150, 150)
        )
        cont_rect = cont_surf.get_rect(
            center=(self.settings.WIDTH // 2, self.settings.HEIGHT - 50)
        )
        surface.blit(cont_surf, cont_rect)

    # -------------- Update --------------
    # ... (Mantenha o resto da classe como estava até chegar no método update)

    # -------------- Update --------------
    def update(self, dt: float) -> None:
        """
        Atualiza a lógica do jogo.
        O Engine chama este método a cada frame.
        """
        if self.state == "tutorial":
            return

        # 1. Processa a fila de transferências pendentes (lógica de envio)
        # Tenta disparar uma formiga por frame se houver pendências
        self._process_pending_transfers()

        # 2. Atualiza produção nas colônias (nascimento de novas formigas)
        self._update_production(dt)

        # 3. Atualiza a IA inimiga
        self.enemy_ai.update(dt)

        # 4. Atualiza animação dos sprites (troca de frames)
        if self.moving_ants:
            self._update_sprite_animation()

        # 5. Atualiza física/movimento das formigas (deslocamento e colisão)
        self._update_ant_movement()

        # 6. Verifica condição de vitória
        vc = self.config.victory_condition or default_victory_condition
        if vc(self.owners, self.colonies):
            self.completed = True
            self.running = False
            self.logger.info("Level '%s' completed", self.config.name)

    @property
    def result_event(self) -> Optional[Event]:
        if self.completed:
            return LevelCompleteEvent(level_name=self.config.name)
        return None
