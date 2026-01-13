import pygame
import sys
from typing import Any, List
from core.interfaces import IClock, IInputHandler, IRenderer


class PygameClock(IClock):
    def __init__(self) -> None:
        self._clock = pygame.time.Clock()

    def tick(self, fps: int) -> float:
        # Retorna dt em segundos
        return self._clock.tick(fps) / 1000.0

    def get_time(self) -> int:
        return pygame.time.get_ticks()


class PygameInput(IInputHandler):
    def poll(self) -> List[pygame.event.Event]:
        return pygame.event.get()


class PygameRenderer(IRenderer):
    def __init__(self, width: int, height: int, title: str) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)

    def render(self, scene: Any) -> None:
        # Assume que a scene sabe se desenhar na surface fornecida
        # Idealmente, o renderer desenharia a cena, mas mantendo compatibilidade
        # com seu LevelScene existente:
        if hasattr(scene, "render"):
            scene.render(self.screen)
        pygame.display.flip()

    def quit(self) -> None:
        pygame.quit()