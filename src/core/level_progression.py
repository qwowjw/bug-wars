"""
Sistema de persistência de progressão de níveis.
Salva o melhor resultado (máximo de estrelas) para cada fase.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional
from src.core.events import LevelResult


class LevelProgressionManager:
    """Gerencia a persistência de progresso entre fases."""

    def __init__(self, data_dir: Optional[Path] = None) -> None:
        self.logger = logging.getLogger(__name__)
        if data_dir is None:
            data_dir = Path(__file__).parent.parent.parent / "data"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.progress_file = self.data_dir / "level_progress.json"
        self._progress: Dict[str, Dict[str, int]] = self._load_progress()

    def _load_progress(self) -> Dict[str, Dict[str, int]]:
        """Carrega o progresso do arquivo JSON."""
        if not self.progress_file.exists():
            self.logger.info("Arquivo de progresso não encontrado. Iniciando novo.")
            return {}

        try:
            with open(self.progress_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.logger.info("Progresso carregado de %s", self.progress_file)
                return data
        except (json.JSONDecodeError, IOError) as e:
            self.logger.warning("Erro ao carregar progresso: %s. Iniciando novo.", e)
            return {}

    def _save_progress(self) -> None:
        """Salva o progresso no arquivo JSON."""
        try:
            with open(self.progress_file, "w", encoding="utf-8") as f:
                json.dump(self._progress, f, indent=2)
                self.logger.debug("Progresso salvo em %s", self.progress_file)
        except IOError as e:
            self.logger.error("Erro ao salvar progresso: %s", e)

    def update_level_result(self, level_id: str, result: LevelResult) -> None:
        """
        Atualiza o resultado de uma fase, mantendo o melhor (máximo de estrelas).

        Args:
            level_id: ID único da fase
            result: LevelResult da tentativa atual
        """
        if level_id not in self._progress:
            self._progress[level_id] = {"stars": 0, "best_score": 0}

        old_stars = self._progress[level_id]["stars"]
        new_stars = result.stars

        # Sempre mantém o máximo de estrelas
        if new_stars > old_stars:
            self._progress[level_id]["stars"] = new_stars
            self.logger.info(
                "Fase '%s': Novo recorde de estrelas: %d", level_id, new_stars
            )

        # Opcionalmente, também salva o melhor score
        old_score = self._progress[level_id].get("best_score", 0)
        if result.score > old_score:
            self._progress[level_id]["best_score"] = result.score

        self._save_progress()

    def get_level_progress(self, level_id: str) -> Dict[str, int]:
        """Retorna o progresso de uma fase específica."""
        return self._progress.get(level_id, {"stars": 0, "best_score": 0})

    def get_all_progress(self) -> Dict[str, Dict[str, int]]:
        """Retorna todo o progresso armazenado."""
        return self._progress.copy()

    def clear_progress(self) -> None:
        """Limpa todo o progresso (útil para reset/debug)."""
        self._progress = {}
        self._save_progress()
        self.logger.info("Progresso limpo.")
