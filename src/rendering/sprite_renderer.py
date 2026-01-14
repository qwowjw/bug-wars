import logging
from typing import Optional, Tuple, Dict
import pygame
from config.settings import Settings
from utils.asset_loader import load_image
from entities.ant_types import ALL_ANT_TYPES


class SpriteRenderer:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)

        self.ant_sprites: Dict[Tuple[str, int], pygame.Surface] = {}

        self.nest_img_ally: Optional[pygame.Surface] = load_image(
            settings.STRUCTURES_DIR / "formigueiro_aliado.png"
        )
        self.nest_img_empty: Optional[pygame.Surface] = load_image(
            settings.STRUCTURES_DIR / "formigueiro_vazio.png"
        )
        self.nest_img_enemy: Optional[pygame.Surface] = load_image(
            settings.STRUCTURES_DIR / "formigueiro_inimigo.png"
        )

        self._scale_structures()
        self._load_dynamic_ant_sprites()

    def _scale_structures(self) -> None:
        """Redimensiona estruturas estáticas."""
        if self.nest_img_ally:
            self.nest_img_ally = pygame.transform.scale(
                self.nest_img_ally, self.settings.NEST_SIZE
            )
        if self.nest_img_empty:
            self.nest_img_empty = pygame.transform.scale(
                self.nest_img_empty, self.settings.NEST_SIZE
            )
        if self.nest_img_enemy:
            self.nest_img_enemy = pygame.transform.scale(
                self.nest_img_enemy, self.settings.NEST_SIZE
            )

    def _load_dynamic_ant_sprites(self) -> None:
        """
        Carrega sprites dinamicamente para todos os tipos definidos em ant_types.py.
        Espera arquivos no formato: {nome_lower}_1.png e {nome_lower}_2.png
        Ex: quenquen_1.png, quenquen_2.png
        """
        for ant_type in ALL_ANT_TYPES:
            name_lower = ant_type.name.lower()

            # Carrega Frame 1
            path1 = self.settings.ANTS_DIR / f"{name_lower}_1.png"
            img1 = load_image(path1)
            if img1:
                img1 = pygame.transform.scale(img1, self.settings.ANT_SIZE)
                self.ant_sprites[(ant_type.name, 0)] = img1
            else:
                self.logger.warning(f"Sprite não encontrado: {path1}. Usando fallback.")

            # Carrega Frame 2
            path2 = self.settings.ANTS_DIR / f"{name_lower}_2.png"
            img2 = load_image(path2)
            if img2:
                img2 = pygame.transform.scale(img2, self.settings.ANT_SIZE)
                self.ant_sprites[(ant_type.name, 1)] = img2
            else:
                # Se não tiver frame 2, usa o 1 se existir
                if img1:
                    self.ant_sprites[(ant_type.name, 1)] = img1

    def draw_ant(
        self,
        surface: pygame.Surface,
        pos: pygame.Vector2,
        angle: float,
        frame_index: int,
        ant_type_name: str,
    ) -> None:
        frame = self.ant_sprites.get((ant_type_name, frame_index), None)

        if not frame:
            frame = self.ant_sprites.get(("Farao", frame_index))

        # Fallback se a imagem não existir (desenha um círculo)
        if frame is None:
            pygame.draw.circle(surface, (200, 200, 50), (int(pos.x), int(pos.y)), 6)
            return

        rotated = pygame.transform.rotate(frame, -angle)
        rect = rotated.get_rect(center=(int(pos.x), int(pos.y)))
        surface.blit(rotated, rect)

    def draw_nest(
        self, surface: pygame.Surface, center: Tuple[float, float], state: str = "ally"
    ) -> None:
        img = None
        if state == "ally":
            img = self.nest_img_ally
        elif state == "empty":
            img = self.nest_img_empty
        elif state == "enemy":
            img = self.nest_img_enemy

        if img:
            rect = img.get_rect(center=(int(center[0]), int(center[1])))
            surface.blit(img, rect)
        else:
            # Fallback visual se imagem falhar
            color = (
                (50, 200, 120)
                if state == "ally"
                else ((200, 60, 60) if state == "enemy" else (120, 120, 120))
            )
            pygame.draw.circle(
                surface,
                color,
                (int(center[0]), int(center[1])),
                self.settings.NEST_SIZE[0] // 2,
            )

    def draw_selection_ring(
        self, surface: pygame.Surface, center: Tuple[int, int]
    ) -> None:
        pygame.draw.circle(
            surface,
            self.settings.SELECTION_COLOR,
            (int(center[0]), int(center[1])),
            self.settings.NEST_SIZE[0] // 2 + 5,
            3,
        )

    def draw_enemy_ring(self, surface: pygame.Surface, center: Tuple[int, int]) -> None:
        pygame.draw.circle(
            surface,
            (200, 60, 60),
            (int(center[0]), int(center[1])),
            self.settings.NEST_SIZE[0] // 2 + 2,
            2,
        )
