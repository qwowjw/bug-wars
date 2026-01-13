"""
Módulo responsável pela Inteligência Artificial das colônias inimigas.
Define perfis de comportamento e a lógica de tomada de decisão para ataques e produção.
"""

import random
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, TYPE_CHECKING, Literal

import pygame

from entities.ant_types import AntType, ALL_ANT_TYPES

if TYPE_CHECKING:
    from core.level_scene import LevelScene
    from entities.colony import Colony


TargetPriority = Literal["closest", "weakest", "random", "player_focus"]


@dataclass
class AIProfile:
    """
    Define a 'personalidade' da IA.

    Attributes:
        name: Nome do perfil (ex: 'Rusher', 'Turtle').
        attack_interval: Tempo médio entre decisões de ataque (segundos).
        min_ants_to_attack: Mínimo de formigas no ninho para considerar um ataque.
        reserve_percentage: Porcentagem (0.0 a 1.0) de formigas a manter para defesa.
        target_priority: Lógica principal para escolha do alvo.
        allowed_ant_types: Lista de tipos de formigas que esta IA pode alternar para produzir.
        aggro_radius: Distância máxima para buscar alvos (None para infinito).
    """

    name: str
    attack_interval: float = 2.0
    min_ants_to_attack: int = 10
    reserve_percentage: float = 0.3
    target_priority: TargetPriority = "closest"
    allowed_ant_types: List[AntType] = field(default_factory=list)
    aggro_radius: Optional[float] = None


class EnemyController:
    """
    Controlador que gerencia as decisões de todas as colônias inimigas na cena.
    """

    def __init__(self, scene: "LevelScene", profile: AIProfile) -> None:
        self.scene = scene
        self.profile = profile
        self.logger = logging.getLogger(__name__)

        # Timer interno para controle de ações
        self.time_since_last_decision: float = 0.0

        # Variação aleatória para que a IA não seja perfeitamente previsível
        self._current_interval = self._get_randomized_interval()

    def _get_randomized_interval(self) -> float:
        """Adiciona uma variação de +/- 20% ao intervalo base."""
        base = self.profile.attack_interval
        return base * random.uniform(0.8, 1.2)

    def update(self, dt: float) -> None:
        """
        Chamado a cada frame pela LevelScene.

        Args:
            dt: Delta time em segundos.
        """
        self.time_since_last_decision += dt

        if self.time_since_last_decision >= self._current_interval:
            self._execute_logic_cycle()
            self.time_since_last_decision = 0.0
            self._current_interval = self._get_randomized_interval()

    def _execute_logic_cycle(self) -> None:
        """Executa um ciclo de decisão para cada colônia inimiga."""

        # Itera por todos os ninhos para encontrar os que pertencem ao inimigo
        for i, owner in enumerate(self.scene.owners):
            if owner != "enemy":
                continue

            colony = self.scene.colonies[i]

            # 1. Decisão de Produção (Opcional: troca o tipo de formiga se houver opções)
            self._manage_production(colony)

            # 2. Decisão de Ataque
            self._attempt_attack(origin_index=i, colony=colony)

    def _manage_production(self, colony: "Colony") -> None:
        """
        Decide se deve trocar o tipo de formiga sendo produzida.
        Lógica simples: alterna aleatoriamente com baixa chance se houver opções.
        """
        if not self.profile.allowed_ant_types:
            return

        # 5% de chance de mudar a produção a cada ciclo de decisão
        if random.random() < 0.05:
            new_type = random.choice(self.profile.allowed_ant_types)
            if new_type != colony.default_ant_type:
                colony.default_ant_type = new_type
                self.logger.debug(f"Colônia alterou produção para {new_type.name}")

    def _attempt_attack(self, origin_index: int, colony: "Colony") -> None:
        """Avalia e executa um ataque a partir de um ninho específico."""

        ant_count = len(colony.ants)

        # Verifica se tem recursos mínimos
        if ant_count < self.profile.min_ants_to_attack:
            return

        # Verifica se já não está enviando um ataque (evita spam excessivo)
        if any(t["origin"] == origin_index for t in self.scene.pending_transfers):
            return

        target_index = self._select_best_target(origin_index)

        if target_index is not None:
            # Calcula quantas formigas enviar
            reserve = int(ant_count * self.profile.reserve_percentage)
            send_amount = ant_count - reserve

            if send_amount > 0:
                self.scene.pending_transfers.append(
                    {
                        "origin": origin_index,
                        "dest": target_index,
                        "remaining": send_amount,
                    }
                )
                self.logger.info(
                    f"IA ({self.profile.name}): Ataque de {origin_index} -> {target_index} com {send_amount} formigas."
                )

    def _select_best_target(self, origin_index: int) -> Optional[int]:
        """Seleciona o melhor alvo baseado no perfil da IA."""
        possible_targets: List[Tuple[int, float]] = []
        origin_pos = pygame.Vector2(self.scene.nest_positions[origin_index])

        for i, pos_tuple in enumerate(self.scene.nest_positions):
            if i == origin_index:
                continue

            # Ignora atacar o próprio time (por enquanto, IA não faz reforço)
            if self.scene.owners[i] == "enemy":
                continue

            target_pos = pygame.Vector2(pos_tuple)
            dist = origin_pos.distance_to(target_pos)

            # Filtra por raio de agressividade
            if self.profile.aggro_radius and dist > self.profile.aggro_radius:
                continue

            score = 0.0

            # Lógica de Pontuação baseada no Perfil
            if self.profile.target_priority == "closest":
                # Quanto menor a distância, maior o score (inverso)
                score = 10000 / (dist + 1)

            elif self.profile.target_priority == "weakest":
                target_ants = len(self.scene.colonies[i].ants)
                # Prioriza ninhos vazios ou com poucas formigas
                score = 1000 / (target_ants + 1)

            elif self.profile.target_priority == "player_focus":
                # Prioriza atacar o jogador ('ally'), depois neutros
                if self.scene.owners[i] == "ally":
                    score = 2000
                else:
                    score = 100
                # Desempate pela distância
                score += 1000 / (dist + 1)

            elif self.profile.target_priority == "random":
                score = random.random() * 100

            possible_targets.append((i, score))

        if not possible_targets:
            return None

        # Retorna o índice com maior score
        possible_targets.sort(key=lambda x: x[1], reverse=True)
        return possible_targets[0][0]


# --- Perfis Predefinidos ---
AI_TURTLE = AIProfile(
    name="Turtle",
    attack_interval=8.0,  # Demora muito para atacar
    min_ants_to_attack=30,  # Acumula muitas formigas
    reserve_percentage=0.8,  # Mantém 80% em casa
    target_priority="closest",
)

AI_BALANCED = AIProfile(
    name="Balanced",
    attack_interval=3.0,
    min_ants_to_attack=12,
    reserve_percentage=0.2,
    target_priority="closest",
    allowed_ant_types=ALL_ANT_TYPES,  # Pode usar qualquer formiga
)

AI_AGGRESSIVE = AIProfile(
    name="Rusher",
    attack_interval=1.5,
    min_ants_to_attack=5,
    reserve_percentage=0.0,  # Kamikaze
    target_priority="player_focus",
    allowed_ant_types=[
        t for t in ALL_ANT_TYPES if t.speed > 50
    ],  # Apenas formigas rápidas
)

AI_EXPANSIONIST = AIProfile(
    name="Expansionist",
    attack_interval=4.0,
    min_ants_to_attack=15,
    reserve_percentage=0.4,
    target_priority="weakest",  # Foca em ninhos vazios primeiro
    allowed_ant_types=ALL_ANT_TYPES,
)
