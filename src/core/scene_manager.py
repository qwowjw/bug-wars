from typing import Any, Optional


class Scene:
    def handle_event(self, event: Any) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: Any) -> None:
        pass


class SceneManager:
    def __init__(self) -> None:
        self.current: Optional[Scene] = None

    def set_scene(self, scene: Scene) -> None:
        self.current = scene

    def handle_event(self, event: Any) -> None:
        if self.current:
            self.current.handle_event(event)

    def update(self, dt: float) -> None:
        if self.current:
            self.current.update(dt)

    def render(self, surface: Any) -> None:
        if self.current:
            self.current.render(surface)
