from dataclasses import dataclass


class Event:
    """Evento base do sistema."""

    pass


@dataclass(frozen=True)
class QuitEvent(Event):
    """Evento global de encerramento da aplicação."""

    pass


@dataclass(frozen=True)
class GameStartEvent(Event):
    """Evento disparado pela Tela Inicial para começar a campanha."""

    pass


@dataclass(frozen=True)
class LevelCompleteEvent(Event):
    """Evento disparado quando uma fase é vencida."""

    level_name: str


class CampaignStartEvent(Event):
    """Evento disparado para iniciar a campanha completa."""

    pass


@dataclass(frozen=True)
class MouseButtonDown(Event):
    pos: tuple[int, int]
    button: int
    shift: bool = False
    ctrl: bool = False


@dataclass(frozen=True)
class KeyDown(Event):
    key: int
    shift: bool = False
    ctrl: bool = False
