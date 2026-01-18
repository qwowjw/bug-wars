"""
Ponto de entrada da aplicação Ant Simulator.
"""

import logging
import sys
from typing import Tuple, List, Callable, Optional

from src.config.settings import Settings
from src.core.app_config import AppConfig
from src.core.engine import Engine, IScene
from src.core.interfaces import IClock, IInputHandler, IRenderer
from src.core.events import Event, GameStartEvent, LevelFinishedEvent, CampaignStartEvent, NextLevelEvent, RetryLevelEvent
from src.core.level_progression import LevelProgressionManager

from src.core.levels_intro import (
    create_intro_config,
    create_intro2_config,
    create_intro3_config,
)
from src.core.levels_campaign import create_level_1_config
from src.core.level_scene import LevelScene
from src.core.level_config import LevelConfig
from src.core.scenes.title_scene import TitleScene
from src.utils.logging_config import configure_logging

from src.adapters.headless_adapter import HeadlessClock, HeadlessInput, HeadlessRenderer

# Tenta importar Pygame apenas se necessário/disponível
try:
    from src.adapters.pygame_adapter import PygameClock, PygameInput, PygameRenderer

    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


def create_adapters(config: AppConfig) -> Tuple[IClock, IInputHandler, IRenderer]:
    """Factory para criação dos adapters baseada na configuração."""
    logger = logging.getLogger("main.factory")

    if config.mode == "interactive":
        if not PYGAME_AVAILABLE:
            raise ImportError(
                "Modo interativo solicitado, mas 'pygame' não está instalado."
            )

        logger.info("Inicializando Pygame Adapters...")
        return (
            PygameClock(),
            PygameInput(),
            PygameRenderer(config.width, config.height, Settings.WINDOW_TITLE),
        )
    else:
        logger.info("Inicializando Headless Adapters...")
        return (HeadlessClock(fixed_dt=0.016), HeadlessInput(), HeadlessRenderer())


def get_initial_scene(config: AppConfig, renderer: IRenderer) -> IScene:
    """Define qual cena inicia o jogo baseada no modo."""
    if config.mode == "interactive":
        # Renderer do Pygame tem o atributo 'screen', mas IRenderer não garante isso.
        # Em um código 100% puro, passaríamos o Renderer inteiro para a Scene,
        # mas para compatibilidade com o TitleScene atual:
        screen = getattr(renderer, "screen", None)
        if screen is None:
            raise RuntimeError("PygameRenderer deve ter um atributo 'screen'")
        return TitleScene(screen)
    else:
        # Headless começa direto na campanha
        settings = Settings()
        cfg = create_level_1_config(settings)
        return LevelScene(settings, cfg)


class CampaignManager:
    """Gerencia o estado da campanha e a transição de fases."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.progression = LevelProgressionManager()
        self.tutorial_creators: List[Callable[[Settings], LevelConfig]] = [
            create_intro_config,
            create_intro2_config,
            create_intro3_config,
        ]
        self.campaign_creators: List[Callable[[Settings], LevelConfig]] = [
            create_level_1_config,
        ]
        self.active_creators: List[Callable[[Settings], LevelConfig]] = []
        self.current_index = 0
        self.current_level_id: Optional[str] = None

    def start_tutorial(self) -> IScene:
        self.active_creators = self.tutorial_creators
        self.current_index = 0
        return self._create_current_level()

    def start_campaign(self) -> IScene:
        self.active_creators = self.campaign_creators
        self.current_index = 0
        return self._create_current_level()

    def retry_level(self) -> IScene:
        """Reinicia o nível atual."""
        return self._create_current_level()

    def next_level(self) -> Optional[IScene]:
        self.current_index += 1
        if self.current_index < len(self.active_creators):
            return self._create_current_level()
        return None

    def _create_current_level(self) -> LevelScene:
        cfg = self.active_creators[self.current_index](self.settings)
        self.current_level_id = cfg.name
        return LevelScene(self.settings, cfg)


def main() -> int:
    # 1. Config e Logging
    config = AppConfig.from_env()
    configure_logging(level=logging.INFO)  # Poderia vir do config.log_level
    logger = logging.getLogger("main")

    # 2. Adapters
    clock, input_handler, renderer = create_adapters(config)

    # 3. Engine
    engine = Engine(config, clock, input_handler, renderer)

    # 4. Estado Global
    game_settings = Settings()
    campaign = CampaignManager(game_settings)

    # Cena Inicial
    current_scene = get_initial_scene(config, renderer)
    engine.set_scene(current_scene)

    logger.info("Sistema pronto. Iniciando Game Loop.")

    try:
        while True:
            engine.run()

            # O Engine parou. Verificamos o motivo através do estado da cena.
            last_scene = engine.current_scene
            if last_scene is None:
                break

            # Recupera resultado usando o novo Protocolo IScene (que tem result_event)
            # ou fallback para verificação manual se a cena não implementou property
            result: Optional[Event] = getattr(last_scene, "result_event", None)

            # Fallback para TitleScene que usa next_action
            if not result and hasattr(last_scene, "next_action"):
                result = getattr(last_scene, "next_action")

            if isinstance(result, GameStartEvent):
                engine.set_scene(campaign.start_tutorial())

            elif isinstance(result, CampaignStartEvent):
                engine.set_scene(campaign.start_campaign())

            elif isinstance(result, LevelFinishedEvent):
                # Salva o resultado da fase
                if campaign.current_level_id:
                    campaign.progression.update_level_result(
                        campaign.current_level_id, result.result
                    )
                    logger.info(
                        "Progresso salvo para '%s': %d estrelas",
                        campaign.current_level_id,
                        result.result.stars,
                    )

                if result.result.victory:
                    # Vitória: tenta ir para a próxima fase
                    next_scene = campaign.next_level()
                    if next_scene:
                        engine.set_scene(next_scene)
                    else:
                        # Fim da playlist de níveis
                        if config.mode == "interactive":
                            # Volta para o título
                            screen = getattr(renderer, "screen", None)
                            if screen is not None:
                                engine.set_scene(TitleScene(screen))
                            else:
                                logger.error("Não foi possível criar TitleScene: renderer sem screen")
                                break
                        else:
                            logger.info("Campanha headless finalizada.")
                            break
                else:
                    # Derrota: permanece na mesma cena (DefeatScene)
                    # DefeatScene pode emitir eventos para repetir ou voltar ao menu
                    pass

            elif isinstance(result, NextLevelEvent):
                # Botão "Próxima" da VictoryScene
                next_scene = campaign.next_level()
                if next_scene:
                    engine.set_scene(next_scene)
                else:
                    # Fim da playlist de níveis
                    if config.mode == "interactive":
                        # Volta para o título
                        screen = getattr(renderer, "screen", None)
                        if screen is not None:
                            engine.set_scene(TitleScene(screen))
                        else:
                            logger.error("Não foi possível criar TitleScene: renderer sem screen")
                            break
                    else:
                        logger.info("Campanha headless finalizada.")
                        break

            elif isinstance(result, RetryLevelEvent):
                # Botão "Repetir" de VictoryScene ou DefeatScene
                retry_scene = campaign.retry_level()
                engine.set_scene(retry_scene)

            else:
                # QuitEvent ou fim sem transição explícita
                break

    except KeyboardInterrupt:
        logger.info("Interrompido pelo usuário.")
    except Exception:
        logger.exception("Erro fatal não tratado.")
        return 1
    finally:
        engine.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
