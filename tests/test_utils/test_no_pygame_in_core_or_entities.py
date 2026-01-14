from pathlib import Path

FILES = [
    Path("src/core/engine.py"),
    Path("src/ai/enemy_controller.py"),
    Path("src/entities/ant.py"),
    Path("src/entities/ant_types.py"),
    Path("src/entities/colony.py"),
    Path("src/entities/nest.py"),
]


def test_no_pygame_import_in_core_logic_and_entities() -> None:
    for file in FILES:
        text = file.read_text(encoding="utf-8")
        assert "import pygame" not in text, f"Unexpected pygame dependency in {file}"
