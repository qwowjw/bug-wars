from typing import List
from src.core.interfaces import IClock, IInputHandler, IRenderer
from src.core.engine import IScene
from src.core.events import Event


class HeadlessClock(IClock):
    def __init__(self, fixed_dt: float = 0.016) -> None:
        self.fixed_dt = fixed_dt
        self.current_time = 0.0

    def tick(self, fps: int) -> float:
        # Simula passagem de tempo determinística
        self.current_time += self.fixed_dt * 1000
        return self.fixed_dt

    def get_time(self) -> int:
        return int(self.current_time)


class HeadlessInput(IInputHandler):
    def poll(self) -> List[Event]:
        return []  # Sem input do usuário no modo headless


class HeadlessRenderer(IRenderer):
    def __init__(self) -> None:
        pass

    def render(self, scene: IScene) -> None:
        pass

    def quit(self) -> None:
        pass
