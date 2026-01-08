import pygame


class SelectionSystem:
    def handle_event(self, event, nests):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for n in nests:
                n.selected = (abs(n.x - mx) < 24 and abs(n.y - my) < 24)
