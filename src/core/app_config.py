"""
Módulo de configuração da aplicação.
Define configurações de runtime imutáveis e tratamento de variáveis de ambiente.
"""

import os
import argparse
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
        Carrega configurações do ambiente.
        CLI > Env Vars > Defaults
        """
        parser = argparse.ArgumentParser(add_help=True)

        parser.add_argument(
            "--headless",
            action="store_true",
            help="Executa a aplicação em modo headless",
        )

        parser.add_argument(
            "--width",
            type=int,
            default=int(os.getenv("ANT_SIM_WIDTH", 800)),
        )

        parser.add_argument(
            "--height",
            type=int,
            default=int(os.getenv("ANT_SIM_HEIGHT", 400)),
        )

        parser.add_argument(
            "--fps",
            type=int,
            default=int(os.getenv("ANT_SIM_FPS", 60)),
        )

        parser.add_argument(
            "--timeout",
            type=float,
            default=float(os.getenv("ANT_SIM_TIMEOUT", 10.0)),
            dest="headless_timeout",
        )

        parser.add_argument(
            "--log-level",
            type=str,
            default=os.getenv("ANT_SIM_LOG_LEVEL", "INFO").upper(),
            choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
        )

        args = parser.parse_args()

        mode: RunMode = "headless" if args.headless else "interactive"

        return cls(
            mode=mode,
            width=args.width,
            height=args.height,
            fps=args.fps,
            log_level=args.log_level,
            headless_timeout=args.headless_timeout,
        )
