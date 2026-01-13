from entities.colony import Colony
from entities.ant_types import farao


def test_colony_produces_with_existing_ants():
    # cria colônia com tipo farao e 10 formigas iniciais
    colony = Colony((0, 0), ant_type=farao)
    colony.spawn_ants(10)

    # produção deve começar: farao.production_time == 6.0
    produced = 0
    # simula passos de 0.5s, até produzir ao menos 1
    dt = 0.5
    elapsed = 0.0
    timeout = 10.0
    while produced == 0 and elapsed < timeout:
        produced = colony.update(dt)
        elapsed += dt

    assert produced >= 1
    assert len(colony.ants) >= 11
