import pygame


class Renderer:
    def __init__(self):
        self.initialized = True

    def draw(self, surface: pygame.Surface):
        raise NotImplementedError
