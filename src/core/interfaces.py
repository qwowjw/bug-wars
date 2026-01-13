"""
Interfaces fundamentais para abstração de I/O e Loop.
"""

from typing import Protocol, Any, runtime_checkable
from core.events import Event

@runtime_checkable
class IClock(Protocol):
    """Protocolo para gerenciamento de tempo."""
    def tick(self, fps: int) -> float:
        """Avança o frame e retorna o delta time em segundos."""
        ...

    def get_time(self) -> int:
        """Retorna o tempo atual em milissegundos."""
        ...


@runtime_checkable
class IInputHandler(Protocol):
    """Protocolo para coleta de eventos."""
    def poll(self) -> list[Any]:
        """Retorna lista de eventos do sistema."""
        ...


@runtime_checkable
class IRenderer(Protocol):
    """Protocolo para renderização de cenas."""
    def render(self, scene: Any, events: list[Event]) -> None:
        """Desenha a cena atual."""
        ...
    
    def quit(self) -> None:
        """Encerra o contexto gráfico."""
        ...
        
