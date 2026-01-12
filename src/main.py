import os
import sys
import logging

try:
    import pygame  # type: ignore
    PYGAME_AVAILABLE = True
except ModuleNotFoundError:
    PYGAME_AVAILABLE = False

# Headless if env var set or `--headless` passed
FORCE_HEADLESS = os.getenv("ANT_SIM_HEADLESS") == "1" or "--headless" in sys.argv

from config.settings import Settings
from utils.logging_config import configure_logging

# configure logging early
configure_logging(level=Settings.LOG_LEVEL)

if PYGAME_AVAILABLE and not FORCE_HEADLESS:
    from core.scene_manager import SceneManager
    from core.level_scene import LevelScene
    from core.levels import create_intro_config, create_level1_config, create_level2_config

    def main():
        logging.getLogger(__name__).info("Starting game (interactive mode)")
        pygame.init()
        settings = Settings()
        screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        pygame.display.set_caption(settings.WINDOW_TITLE)

        manager = SceneManager()

        intro_cfg = create_intro_config(settings)
        level1_cfg = create_level1_config(settings)
        level2_cfg = create_level2_config(settings)

        # Run intro
        intro_scene = LevelScene(screen, settings, intro_cfg)
        manager.set_scene(intro_scene)
        intro_scene.run()

        # On victory, transition to level1 then level2
        if not intro_scene.running:
            logging.getLogger(__name__).info("Transitioning to level1")
            level1_scene = LevelScene(screen, settings, level1_cfg)
            manager.set_scene(level1_scene)
            level1_scene.run()

            if not level1_scene.running:
                logging.getLogger(__name__).info("Transitioning to level2")
                level2_scene = LevelScene(screen, settings, level2_cfg)
                manager.set_scene(level2_scene)
                level2_scene.run()

        pygame.quit()

else:
    # Headless/demo mode: run a simple simulation of the intro level production
    from core.levels import create_intro_config
    from entities.colony import Colony
    from entities.ant_types import farao

    def main():
        logging.getLogger(__name__).info("Running in headless demo mode")
        settings = Settings()
        cfg = create_intro_config(settings)

        colonies = []
        for idx, pos in enumerate(cfg.nest_positions):
            ant_type = farao
            col = Colony(pos, ant_type=ant_type)
            if cfg.initial_owners[idx] != "empty" and cfg.initial_counts[idx] > 0:
                col.spawn_ants(int(cfg.initial_counts[idx]))
            colonies.append(col)

        # simple production loop (safe to parallelize in real run)
        dt = 0.5
        elapsed = 0.0
        timeout = 10.0
        while elapsed < timeout:
            produced = 0
            for c in colonies:
                produced += c.update(dt)
            logging.getLogger(__name__).debug("Headless tick produced=%d", produced)
            # victory condition: all nests have at least one ally ant
            if all(len(c.ants) > 0 for c in colonies):
                logging.getLogger(__name__).info("Headless: victory achieved")
                break
            elapsed += dt

        logging.getLogger(__name__).info("Headless demo finished")

if __name__ == "__main__":
    main()
