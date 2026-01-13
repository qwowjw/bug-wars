import pygame
from typing import List
from entities.nest import Nest


class SelectionSystem:
    def handle_event(self, event: pygame.event.Event, nests: List[Nest]) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for n in nests:
                n.selected = abs(n.x - mx) < 24 and abs(n.y - my) < 24
