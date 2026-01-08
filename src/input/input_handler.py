import pygame


class InputHandler:
    def poll(self):
        return pygame.event.get()
