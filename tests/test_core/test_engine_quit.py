from typing import Any, List

from core.app_config import AppConfig
from core.engine import Engine, IScene
from core.interfaces import IClock, IInputHandler, IRenderer
from core.events import QuitEvent
from adapters.headless_adapter import HeadlessClock


class TestInput(IInputHandler):
    def __init__(self) -> None:
        self._sent = False

    def poll(self) -> List[Any]:
        if not self._sent:
            self._sent = True
            return [QuitEvent()]
        return []


class TestRenderer(IRenderer):
    def render(self, scene: Any) -> None:
        # No-op
        pass

    def quit(self) -> None:
        pass


class TestScene(IScene):
    def __init__(self) -> None:
        self.running = True
        self.updates = 0

    def handle_event(self, event: Any) -> None:
        # Scene does not stop itself; Engine handles QuitEvent
        pass

    def update(self, dt: float) -> None:
        self.updates += 1

    def render(self, surface: Any) -> None:
        pass


def test_engine_stops_on_quit_event() -> None:
    config = AppConfig(
        mode="headless",
        width=800,
        height=600,
        fps=60,
        log_level="INFO",
        headless_timeout=5.0,
    )
    clock: IClock = HeadlessClock(fixed_dt=0.016)
    input_handler: IInputHandler = TestInput()
    renderer: IRenderer = TestRenderer()

    engine = Engine(
        config=config, clock=clock, input_handler=input_handler, renderer=renderer
    )
    scene = TestScene()
    engine.set_scene(scene)

    engine.run()

    # Deve ter atualizado ao menos 1 vez e parar rapidamente.
    assert scene.updates >= 1
    assert scene.updates < 1000
