"""
Módulo de configuração da aplicação.
Define configurações de runtime imutáveis e tratamento de variáveis de ambiente.
"""

import os
import sys
from dataclasses import dataclass
from typing import Literal

RunMode = Literal["interactive", "headless"]


@dataclass(frozen=True)
class AppConfig:
    """Configuração de runtime da aplicação."""

    mode: RunMode
    width: int
    height: int
    fps: int
    log_level: str
    headless_timeout: float

    @classmethod
    def from_env(cls) -> "AppConfig":
        """
        Carrega configurações do ambiente (CLI args e Env Vars).
        Prioriza argumentos de linha de comando sobre variáveis de ambiente.
        """
        # Determinação do modo
        arg_headless = "--headless" in sys.argv
        env_headless = os.getenv("ANT_SIM_HEADLESS") == "1"
        mode: RunMode = "headless" if (arg_headless or env_headless) else "interactive"

        # Parsing seguro de inteiros
        try:
            width = int(os.getenv("ANT_SIM_WIDTH", "800"))
            height = int(os.getenv("ANT_SIM_HEIGHT", "400"))
            fps = int(os.getenv("ANT_SIM_FPS", "60"))
            timeout = float(os.getenv("ANT_SIM_TIMEOUT", "10.0"))
        except ValueError as e:
            # Em produção, logaríamos isso e usaríamos defaults ou falharíamos
            print(f"Erro ao analisar configuração numérica: {e}. Usando defaults.")
            width, height, fps, timeout = 800, 400, 60, 10.0

        return cls(
            mode=mode,
            width=width,
            height=height,
            fps=fps,
            log_level=os.getenv("ANT_SIM_LOG_LEVEL", "INFO").upper(),
            headless_timeout=timeout,
        )
