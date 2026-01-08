import os
from typing import Optional
import pygame


def load_image(path: str) -> Optional[pygame.Surface]:
    """
    Load an image with fallback lookups:
    - ant_simulator/assets/...
    - project_root/assets/...
    """
    try:
        candidates = []
        if os.path.isabs(path):
            candidates.append(path)
        else:
            # Base = ant_simulator (three levels up from this file)
            base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            candidates.append(os.path.join(base, path))
            # Fallback to project root (one level above ant_simulator)
            candidates.append(os.path.join(os.path.dirname(base), path))

        for p in candidates:
            if os.path.exists(p):
                return pygame.image.load(p).convert_alpha()
        return None
    except Exception:
        return None
