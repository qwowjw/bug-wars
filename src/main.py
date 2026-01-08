import pygame
from config.settings import Settings
from core.game_engine import GameEngine


def main():
    pygame.init()
    settings = Settings()
    screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption(settings.WINDOW_TITLE)

    engine = GameEngine(screen, settings)
    engine.run()

    pygame.quit()


if __name__ == "__main__":
    main()
