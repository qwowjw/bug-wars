import pytest
from typing import Tuple

from config.settings import Settings
from core.levels_intro import create_intro_config
from core.level_scene import LevelScene
from core.events import MouseButtonDown

pytest.importorskip("pygame")
import pygame


def _center_of(scene: LevelScene, idx: int) -> Tuple[int, int]:
    rect = scene.nest_rects[idx]
    return (rect.centerx, rect.centery)


def test_levelscene_handles_generic_mouse_events_selection_and_transfer() -> None:
    pygame.init()
    try:
        settings = Settings()
        cfg = create_intro_config(settings)

        scene = LevelScene(settings, cfg)

        # initially, ally at index 0 has ants
        assert scene.owners[0] == "ally"
        assert len(scene.colonies[0].ants) > 0

        # click on ally nest to select
        pos0 = _center_of(scene, 0)
        scene.handle_event(MouseButtonDown(pos=pos0, button=1, shift=False, ctrl=False))
        assert scene.selected_nest_indices == {0}

        # click destination (other nest) without shift => enqueue transfer of all available
        pos1 = _center_of(scene, 1)
        scene.handle_event(MouseButtonDown(pos=pos1, button=1, shift=False, ctrl=False))

        # one transfer should be queued from 0 -> 1
        assert any(t["origin"] == 0 and t["dest"] == 1 for t in scene.pending_transfers)
    finally:
        pygame.quit()
