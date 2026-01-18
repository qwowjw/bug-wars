"""
Motor principal da aplicação.
Responsável pelo Loop de Jogo (Game Loop) agnóstico de plataforma.
"""

import logging
from typing import Any, Optional, Protocol, runtime_checkable

from src.core.interfaces import IClock, IInputHandler, IRenderer
from src.core.app_config import AppConfig
from src.core.events import QuitEvent, Event, LevelFinishedEvent
from enum import Enum, auto


class EngineExit(Enum):
    QUIT = auto()
    SCENE_FINISHED = auto()



@runtime_checkable
class IScene(Protocol):
    """Protocolo que uma Cena deve implementar para rodar no Engine."""

    running: bool

    def update(self, dt: float) -> None: ...
    def handle_event(self, event: Any) -> None: ...
    def render(self, surface: Any) -> None: ...

    @property
    def result_event(self) -> Optional["Event"]: ...


class Engine:
    """
    Gerencia o ciclo de vida da aplicação.
    Orquestra Tempo, Input, Lógica e Renderização.
    """

    def __init__(
        self,
        config: AppConfig,
        clock: IClock,
        input_handler: IInputHandler,
        renderer: IRenderer,
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.clock = clock
        self.input_handler = input_handler
        self.renderer = renderer
        self.current_scene: Optional[IScene] = None
        self._running = False

    def set_scene(self, scene: IScene) -> None:
        self.current_scene = scene

    def run(self) -> EngineExit:
        """Inicia o loop principal."""
        if not self.current_scene:
            self.logger.error("Nenhuma cena definida para o Engine.")
            return EngineExit.QUIT
        self.logger.info("Iniciando Engine no modo: %s", self.config.mode)
        self._running = True

        # Controle de segurança para modo headless (timeout)
        start_time = self.clock.get_time()

        try:
            while self._running and self.current_scene.running:
                # 1. Controle de Tempo
                dt = self.clock.tick(self.config.fps)

                # 2. Input
                events = self.input_handler.poll()
                for event in events:
                    # Intercepta um encerramento global desacoplado de pygame
                    if isinstance(event, QuitEvent):
                        self._running = False
                        return EngineExit.QUIT

                    self.current_scene.handle_event(event)

                # 3. Update (Lógica)
                self.current_scene.update(dt)

                # 4. Render
                self.renderer.render(self.current_scene)

                # 5. Verificar eventos de conclusão da cena
                result_event = self.current_scene.result_event
                if result_event:
                    self._handle_scene_result(result_event)

                # 6. Verificações Headless (Timeout)
                if self.config.mode == "headless":
                    elapsed = (self.clock.get_time() - start_time) / 1000.0
                    if elapsed > self.config.headless_timeout:
                        self.logger.info(
                            "Headless: Timeout atingido (%.1fs). Encerrando.", elapsed
                        )
                        self._running = False
                        return EngineExit.QUIT

        except KeyboardInterrupt:
            self.logger.info("Interrupção pelo usuário (Ctrl+C).")
            return EngineExit.QUIT
        except Exception:
            self.logger.exception("Falha crítica no Loop do Engine.")
            raise
        finally:
            self.logger.info("Cena finalizada ou Engine pausado.")

        return EngineExit.SCENE_FINISHED

    def _handle_scene_result(self, event: Event) -> None:
        """Processa eventos de conclusão de cena e roteia para as próximas cenas."""
        if isinstance(event, LevelFinishedEvent):
            # Roteamento de cenas baseado no resultado da fase
            if event.result.victory:
                from src.core.scenes.victory_scene import VictoryScene

                self.current_scene = VictoryScene(event.result)
                self.logger.info(
                    "Mudando para VictoryScene. Stars: %d, Score: %d",
                    event.result.stars,
                    event.result.score,
                )
            else:
                from src.core.scenes.defeat_scene import DefeatScene

                self.current_scene = DefeatScene()
                self.logger.info("Mudando para DefeatScene.")

    def shutdown(self) -> None:
        """Encerra explicitamente os recursos do engine."""
        self.logger.info("Shutdown do Engine solicitado.")
        self.renderer.quit()
