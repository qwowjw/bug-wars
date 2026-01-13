import pygame


class Renderer:
    def __init__(self) -> None:
        self.initialized = True

    def draw(self, surface: pygame.Surface) -> None:
        raise NotImplementedError
