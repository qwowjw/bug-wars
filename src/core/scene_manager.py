class Scene:
    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def render(self, surface):
        pass


class SceneManager:
    def __init__(self):
        self.current = None

    def set_scene(self, scene: Scene):
        self.current = scene

    def handle_event(self, event):
        if self.current:
            self.current.handle_event(event)

    def update(self, dt):
        if self.current:
            self.current.update(dt)

    def render(self, surface):
        if self.current:
            self.current.render(surface)
