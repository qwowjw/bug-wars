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
