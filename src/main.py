"""
Ponto de entrada (Entrypoint) da aplicação Ant Simulator.
Responsável pelo bootstrap, injeção de dependências e inicialização do Engine.

Uso:
    python src/main.py [--headless]
"""

import sys
import logging
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import Settings
from core.app_config import AppConfig
from core.engine import Engine
from core.levels_intro import (
    create_intro_config,
    create_intro2_config,
    create_intro3_config,
)
from core.levels_campaign import (
    create_level_1_config,
)
from core.level_scene import LevelScene
from core.events import GameStartEvent, LevelCompleteEvent, CampaignStartEvent
from core.scenes.title_scene import TitleScene
from utils.logging_config import configure_logging
from core.interfaces import IClock, IInputHandler, IRenderer

# Adapters
try:
    from adapters.pygame_adapter import PygameClock, PygameInput, PygameRenderer

    PYGAME_INSTALLED = True
except ImportError:
    PYGAME_INSTALLED = False

from adapters.headless_adapter import HeadlessClock, HeadlessInput, HeadlessRenderer


def main() -> None:
    # 1. Configuração de ambiente
    config = AppConfig.from_env()

    # 2. Logging
    log_level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
    }
    configure_logging(level=log_level_map.get(config.log_level, logging.INFO))
    logger = logging.getLogger("main")

    # 3. Adapters
    clock: IClock
    input_handler: IInputHandler
    renderer: IRenderer
    if config.mode == "interactive":
        if not PYGAME_INSTALLED:
            logger.critical(
                "Modo interativo solicitado, mas pygame não está instalado."
            )
            sys.exit(1)

        logger.info("Inicializando Pygame...")
        clock = PygameClock()
        input_handler = PygameInput()
        renderer = PygameRenderer(config.width, config.height, Settings.WINDOW_TITLE)
        screen_surface = renderer.screen
    else:
        logger.info("Inicializando modo headless...")
        clock = HeadlessClock(fixed_dt=0.016)
        input_handler = HeadlessInput()
        renderer = HeadlessRenderer()

        import pygame

        screen_surface = pygame.Surface((config.width, config.height))

    # 4. Engine
    try:
        engine = Engine(
            config=config,
            clock=clock,
            input_handler=input_handler,
            renderer=renderer,
        )

        game_settings = Settings()

        # Definição do tutorial
        tutorial_creators = [
            create_intro_config,
            create_intro2_config,
            create_intro3_config,
        ]

        # Definição da campanha completa
        level_creators = [
            create_level_1_config,
        ]

        current_level_index = 0

        # Cena inicial: Title
        title_scene = TitleScene(screen_surface)
        engine.set_scene(title_scene)

        logger.info("Sistema pronto. Iniciando loop principal.")

        # 5. Loop de orquestração de cenas
        while True:
            engine.run()

            last_scene = engine.current_scene
            next_event = getattr(last_scene, "next_action", None)

            if last_scene is not None:
                result_event = getattr(last_scene, "result_event", None)
                if result_event:
                    next_event = result_event

            # Transições
            if isinstance(next_event, GameStartEvent):
                active_creators = tutorial_creators
                current_level_index = 0
                cfg = active_creators[current_level_index](game_settings)
                engine.set_scene(LevelScene(screen_surface, game_settings, cfg))

            elif isinstance(next_event, CampaignStartEvent):
                active_creators = level_creators
                current_level_index = 0
                cfg = active_creators[current_level_index](game_settings)
                engine.set_scene(LevelScene(screen_surface, game_settings, cfg))

            elif isinstance(next_event, LevelCompleteEvent):
                current_level_index += 1

                if current_level_index < len(active_creators):
                    cfg = active_creators[current_level_index](game_settings)
                    engine.set_scene(LevelScene(screen_surface, game_settings, cfg))
                else:
                    engine.set_scene(TitleScene(screen_surface))

            else:
                # Cena terminou sem evento explícito (quit real)
                break

    except Exception:
        logger.exception("Aplicação encerrada inesperadamente.")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
