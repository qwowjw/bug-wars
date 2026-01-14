import pygame
from typing import List
from core.interfaces import IClock, IInputHandler, IRenderer
from core.events import QuitEvent, MouseButtonDown, KeyDown, Event
from core.engine import IScene


class PygameClock(IClock):
    def __init__(self) -> None:
        self._clock = pygame.time.Clock()

    def tick(self, fps: int) -> float:
        # Retorna dt em segundos
        return self._clock.tick(fps) / 1000.0

    def get_time(self) -> int:
        return pygame.time.get_ticks()


class PygameInput(IInputHandler):
    def poll(self) -> List[Event]:
        out: List[Event] = []
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                out.append(QuitEvent())
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                mods = pygame.key.get_mods()
                shift = bool(mods & pygame.KMOD_SHIFT)
                ctrl = bool(mods & (pygame.KMOD_CTRL | pygame.KMOD_META))
                pos = (int(ev.pos[0]), int(ev.pos[1])) if hasattr(ev, "pos") else (0, 0)
                btn = int(getattr(ev, "button", 0))
                out.append(MouseButtonDown(pos=pos, button=btn, shift=shift, ctrl=ctrl))
            elif ev.type == pygame.KEYDOWN:
                mods = int(getattr(ev, "mod", pygame.key.get_mods()))
                shift = bool(mods & pygame.KMOD_SHIFT)
                ctrl = bool(mods & (pygame.KMOD_CTRL | pygame.KMOD_META))
                key = int(getattr(ev, "key", 0))
                out.append(KeyDown(key=key, shift=shift, ctrl=ctrl))
        return out


class PygameRenderer(IRenderer):
    def __init__(self, width: int, height: int, title: str) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)

    def render(self, scene: IScene) -> None:
        if hasattr(scene, "render"):
            scene.render(self.screen)
        pygame.display.flip()

    def quit(self) -> None:
        pygame.quit()
