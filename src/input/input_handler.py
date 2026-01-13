import pygame
from typing import List


class InputHandler:
    def poll(self) -> List[pygame.event.Event]:
        return pygame.event.get()
