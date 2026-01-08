import os
from typing import Optional, Tuple
import pygame
from config.settings import Settings
from utils.asset_loader import load_image


class SpriteRenderer:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.ant_frame1: Optional[pygame.Surface] = load_image(os.path.join(settings.ANTS_DIR, "formiga-operaria.png"))
        self.ant_frame2: Optional[pygame.Surface] = load_image(os.path.join(settings.ANTS_DIR, "formiga-operaria2.png"))
        self.nest_img: Optional[pygame.Surface] = load_image(os.path.join(settings.STRUCTURES_DIR, "formigueiro.png"))

        if self.ant_frame1:
            self.ant_frame1 = pygame.transform.scale(self.ant_frame1, self.settings.ANT_SIZE)
        if self.ant_frame2:
            self.ant_frame2 = pygame.transform.scale(self.ant_frame2, self.settings.ANT_SIZE)
        if self.nest_img:
            self.nest_img = pygame.transform.scale(self.nest_img, self.settings.NEST_SIZE)

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


    def draw_nest(self, surface: pygame.Surface, center: Tuple[float, float]) -> None:
        if self.nest_img:
            rect = self.nest_img.get_rect(center=(int(center[0]), int(center[1])))
            surface.blit(self.nest_img, rect)
        else:
            pygame.draw.circle(surface, (50, 200, 120), (int(center[0]), int(center[1])), self.settings.NEST_SIZE[0] // 2)
