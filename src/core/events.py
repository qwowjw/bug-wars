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

@dataclass(frozen=True)
class LevelResult:
    """Resultado imutável de uma fase completa."""

    victory: bool
    time_spent: float
    score: int
    stars: int


@dataclass(frozen=True)
class LevelFinishedEvent(Event):
    """Evento disparado quando uma fase é terminada (vitória ou derrota)."""

    result: LevelResult


@dataclass(frozen=True)
class NextLevelEvent(Event):
    """Evento para prosseguir para a próxima fase."""

    pass


@dataclass(frozen=True)
class RetryLevelEvent(Event):
    """Evento para reiniciar a fase atual."""

    pass
