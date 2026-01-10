import os
import sys

try:
    import pygame  # type: ignore
    PYGAME_AVAILABLE = True
except ModuleNotFoundError:
    PYGAME_AVAILABLE = False

# Force headless/demo mode even if pygame is installed by setting env var
# `ANT_SIM_HEADLESS=1` or passing `--headless` on the command line.
FORCE_HEADLESS = os.getenv("ANT_SIM_HEADLESS") == "1" or "--headless" in sys.argv


if PYGAME_AVAILABLE and not FORCE_HEADLESS:
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


else:
    # Headless/demo mode when pygame isn't installed: simulate nest production
    def main():
        import time
        from entities.ant_types import farao
        from entities.ant import Ant

        print("Pygame not available — running headless production demo (Faraó)")

        # Simple nest simulation: if there's at least one ant in the nest,
        # production accumulates and produces new ants every `production_time` seconds.
        nest_ants = []

        # seed the nest with one Faraó (as requested)
        initial = Ant((0, 0), farao)
        nest_ants.append(initial)

        production_progress = 0.0
        production_time = float(farao.production_time)
        tick = 0.5
        total_simulation = 20.0
        elapsed = 0.0

        while elapsed < total_simulation:
            has_any = len(nest_ants) > 0
            if has_any:
                production_progress += tick
            # print status
            status = (
                f"t={elapsed:.1f}s | nest_count={len(nest_ants)} | "
                f"production_active={has_any} | progress={production_progress:.1f}/{production_time}s"
            )
            print(status)

            # produce when ready
            while production_progress >= production_time and has_any:
                production_progress -= production_time
                new_ant = Ant((0, 0), farao)
                nest_ants.append(new_ant)
                print(f"Produced new {new_ant.type.name} — total now {len(nest_ants)}")

            time.sleep(tick)
            elapsed += tick

        print("Simulation finished. Final nest count:", len(nest_ants))


if __name__ == "__main__":
    main()
