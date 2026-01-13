"""
Motor principal da aplicação.
Responsável pelo Loop de Jogo (Game Loop) agnóstico de plataforma.
"""

import logging
from typing import Optional, Protocol, runtime_checkable

from core.interfaces import IClock, IInputHandler, IRenderer
from core.app_config import AppConfig


@runtime_checkable
class IScene(Protocol):
    """Protocolo que uma Cena deve implementar para rodar no Engine."""
    running: bool
    def update(self, dt: float) -> None: ...
    def handle_event(self, event: any) -> None: ...
    def render(self, surface: any) -> None: ...


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

    def run(self) -> None:
        """Inicia o loop principal."""
        if not self.current_scene:
            self.logger.error("Nenhuma cena definida para o Engine.")
            return

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
                    # Permite que o Engine intercepte Quit global, se necessário
                    if hasattr(event, 'type'):
                        # Pequeno acoplamento com estrutura de evento pygame
                        # para manter compatibilidade com sistemas existentes,
                        # mas poderia ser abstraído.
                        import pygame
                        if event.type == pygame.QUIT:
                            self._running = False
                    
                    self.current_scene.handle_event(event)

                # 3. Update (Lógica)
                self.current_scene.update(dt)

                # 4. Render
                self.renderer.render(self.current_scene)

                # 5. Verificações Headless (Timeout)
                if self.config.mode == "headless":
                    elapsed = (self.clock.get_time() - start_time) / 1000.0
                    if elapsed > self.config.headless_timeout:
                        self.logger.info("Headless: Timeout atingido (%.1fs). Encerrando.", elapsed)
                        self._running = False

        except KeyboardInterrupt:
            self.logger.info("Interrupção pelo usuário (Ctrl+C).")
        except Exception:
            self.logger.exception("Falha crítica no Loop do Engine.")
            raise
        finally:
            self.logger.info("Cena finalizada ou Engine pausado.")
            
    def shutdown(self) -> None:
        """Encerra explicitamente os recursos do engine."""
        self.logger.info("Shutdown do Engine solicitado.")
        self.renderer.quit()