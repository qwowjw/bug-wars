import logging
from typing import Optional


def configure_logging(level: Optional[int] = None) -> None:
    lvl = level if level is not None else logging.INFO
    logging.basicConfig(
        level=lvl,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
