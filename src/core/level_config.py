from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Callable, Union, Literal
from pathlib import Path

# Tipo para definir segmentos de texto: ("Texto", (R, G, B)) ou apenas "Texto" (branco padrão)
TextSegment = Union[str, Tuple[str, Tuple[int, int, int]]]
# Tipo para instrução: pode ser uma linha de texto ou um caminho para imagem (ícone)
InstructionElement = Union[TextSegment, Path]

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
    initial_owners: List[str] # "ally", "enemy", "empty"
    ant_types: Optional[List[str]] = None
    randomize_positions: bool = False
    enemy_produces: bool = False
    # Callable de vitória
    victory_condition: Optional[Callable] = None
    # Novo campo opcional
    tutorial: Optional[TutorialConfig] = None

    def validate(self) -> None:
        if len(self.nest_positions) != len(self.initial_counts):
            raise ValueError("Número de posições de ninho não corresponde ao número de contagens iniciais.")
        if len(self.nest_positions) != len(self.initial_owners):
            raise ValueError("Número de posições de ninho não corresponde ao número de proprietários iniciais.")