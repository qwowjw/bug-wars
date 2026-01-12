import os
from typing import Optional, Tuple
import pygame
from config.settings import Settings
from utils.asset_loader import load_image


class SpriteRenderer:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.ant_frame1: Optional[pygame.Surface] = load_image(os.path.join(settings.ANTS_DIR, "faraoh_1.png"))
        self.ant_frame2: Optional[pygame.Surface] = load_image(os.path.join(settings.ANTS_DIR, "faraoh_2.png"))
        # support different nest images: allied and empty
        self.nest_img_ally: Optional[pygame.Surface] = load_image(os.path.join(settings.STRUCTURES_DIR, "formigueiro_aliado.png"))
        self.nest_img_empty: Optional[pygame.Surface] = load_image(os.path.join(settings.STRUCTURES_DIR, "formigueiro_vazio.png"))
        # enemy nest image (optional)
        self.nest_img_enemy: Optional[pygame.Surface] = load_image(os.path.join(settings.STRUCTURES_DIR, "formigueiro_inimigo.png"))

        if self.ant_frame1:
            self.ant_frame1 = pygame.transform.scale(self.ant_frame1, self.settings.ANT_SIZE)
        if self.ant_frame2:
            self.ant_frame2 = pygame.transform.scale(self.ant_frame2, self.settings.ANT_SIZE)
        if self.nest_img_ally:
            self.nest_img_ally = pygame.transform.scale(self.nest_img_ally, self.settings.NEST_SIZE)
        if self.nest_img_empty:
            self.nest_img_empty = pygame.transform.scale(self.nest_img_empty, self.settings.NEST_SIZE)
        if self.nest_img_enemy:
            self.nest_img_enemy = pygame.transform.scale(self.nest_img_enemy, self.settings.NEST_SIZE)

    def draw_ant(
        self,
        surface: pygame.Surface,
        pos: pygame.Vector2,
        angle: float,
        frame_index: int,
    ) -> None:
        frame = self.ant_frame1 if frame_index == 0 else self.ant_frame2

        x, y = int(pos.x), int(pos.y)

        if frame:
            rotated = pygame.transform.rotate(frame, -angle)
            rect = rotated.get_rect(center=(x, y))
            surface.blit(rotated, rect)
        else:
            pygame.draw.circle(surface, (200, 200, 50), (x, y), 6)


    def draw_nest(self, surface: pygame.Surface, center: Tuple[float, float], state: str = "ally") -> None:
        """Draw nest image depending on state: 'ally' or 'empty'."""
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
            # fallback: colored circle (green for ally, gray for empty)
            color = (50, 200, 120) if state == "ally" else ((200, 60, 60) if state == "enemy" else (120, 120, 120))
            pygame.draw.circle(surface, color, (int(center[0]), int(center[1])), self.settings.NEST_SIZE[0] // 2)
