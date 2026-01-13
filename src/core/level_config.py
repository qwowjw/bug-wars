from dataclasses import dataclass
from typing import List, Tuple, Optional, Callable, Union, Literal, TYPE_CHECKING
from pathlib import Path
from ai.enemy_controller import AIProfile

# Tipo para definir segmentos de texto: ("Texto", (R, G, B)) ou apenas "Texto" (branco padrão)
TextSegment = Union[str, Tuple[str, Tuple[int, int, int]]]
# Tipo para instrução: pode ser uma linha de texto ou um caminho para imagem (ícone)
InstructionElement = Union[TextSegment, Path]

# Tipo de dono de ninho
Owner = Literal["ally", "enemy", "empty"]

if TYPE_CHECKING:
    from entities.colony import Colony


@dataclass(frozen=True)
class TutorialConfig:
    """Configuração das instruções de tutorial de uma fase."""

    title: str
    # Lista de linhas, onde cada linha é uma lista de elementos (texto colorido ou imagem)
    lines: List[List[InstructionElement]]


@dataclass(frozen=True)
class LevelConfig:
    name: str
    nest_positions: List[Tuple[int, int]]
    initial_counts: List[int]
    initial_owners: List[str]  # "ally", "enemy", "empty"

    ant_types: Optional[List[str]] = None

    randomize_positions: bool = False
    enemy_produces: bool = False
    victory_condition: Optional[Callable[[List[Owner], List["Colony"]], bool]] = None
    tutorial: Optional[TutorialConfig] = None

    ai_profile: Optional[AIProfile] = None

    def validate(self) -> None:
        """Valida se as listas de configuração têm tamanhos consistentes."""
        n = len(self.nest_positions)

        if len(self.initial_counts) != n:
            raise ValueError(
                f"initial_counts (len={len(self.initial_counts)}) deve ter o mesmo tamanho de nest_positions (len={n})."
            )

        if len(self.initial_owners) != n:
            raise ValueError(
                f"initial_owners (len={len(self.initial_owners)}) deve ter o mesmo tamanho de nest_positions (len={n})."
            )
        if self.ant_types is not None and len(self.ant_types) != n:
            raise ValueError(
                f"ant_types (len={len(self.ant_types)}) deve ter o mesmo tamanho de nest_positions (len={n})."
            )
