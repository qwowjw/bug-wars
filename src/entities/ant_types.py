from .ant import AntType


# Formigas potes de mel
pote_de_mel = AntType(
    name="PoteDeMel",
    armor=0.2,
    poison_resistance=0.1,
    range=6.0,
    dps=0.2,
    special_effect={"type": "storage", "capacity": 50},
    aggressiveness=0.1,
    production_time=20.0,
    speed=30.0,
    crit_chance=0.01,
    crit_multiplier=1.2,
)


# Formigas cortadeiras quénquén — soldados e operárias
cortadeira_soldado = AntType(
    name="CortadeiraSoldado",
    armor=2.0,
    poison_resistance=0.2,
    range=6.0,
    dps=6.0,
    special_effect={"type": "bite", "location": "head"},
    aggressiveness=0.6,
    production_time=25.0,
    speed=40.0,
    crit_chance=0.08,
    crit_multiplier=1.5,
)

cortadeira_operaria = AntType(
    name="CortadeiraOperaria",
    armor=0.8,
    poison_resistance=0.15,
    range=5.0,
    dps=2.0,
    special_effect={"type": "grab_legs", "chance": 0.35, "duration": 2.0},
    aggressiveness=0.4,
    production_time=12.0,
    speed=55.0,
    crit_chance=0.03,
    crit_multiplier=1.3,
)


# Formigas faraó
farao = AntType(
    name="Farao",
    armor=0.1,
    poison_resistance=0.05,
    range=6.0,
    dps=0.4,
    special_effect={"type": "contamination", "dot": 0.3, "duration": 8.0, "chance": 0.15},
    aggressiveness=0.5,
    production_time=6.0,
    speed=45.0,
    crit_chance=0.02,
    crit_multiplier=1.25,
)


# Inimigas independentes
correicao = AntType(
    name="Correicao",
    armor=0.3,
    poison_resistance=0.1,
    range=6.0,
    dps=0.8,
    special_effect={"type": "swarm_bonus", "bonus": "number_based"},
    aggressiveness=0.5,
    production_time=0.0,
    speed=80.0,
    crit_chance=0.02,
    crit_multiplier=1.1,
)

argentina = AntType(
    name="Argentina",
    armor=0.4,
    poison_resistance=0.25,
    range=6.0,
    dps=1.5,
    special_effect={"type": "chemical_injection", "desmembramento_chance": 0.12},
    aggressiveness=0.9,
    production_time=8.0,
    speed=65.0,
    crit_chance=0.12,
    crit_multiplier=1.6,
)

fogo = AntType(
    name="Fogo",
    armor=1.0,
    poison_resistance=0.3,
    range=7.0,
    dps=3.0,
    special_effect={"type": "burn", "dot": 1.0, "duration": 6.0, "aoe": True},
    aggressiveness=0.7,
    production_time=18.0,
    speed=75.0,
    crit_chance=0.07,
    crit_multiplier=1.4,
)


# Export list
ALL_ANT_TYPES = [
    pote_de_mel,
    cortadeira_soldado,
    cortadeira_operaria,
    farao,
    correicao,
    argentina,
    fogo,
]

# Quenquen: enemy invader type
Quenquen = AntType(
    name="Quenquen",
    armor=0.6,
    poison_resistance=0.1,
    range=6.0,
    dps=1.2,
    special_effect={"type": "raid"},
    aggressiveness=0.8,
    production_time=6.0,
    speed=50.0,
    crit_chance=0.05,
    crit_multiplier=1.2,
)

ALL_ANT_TYPES.append(Quenquen)
    

# Map names to instances for lookup by Settings
ANT_TYPES_BY_NAME = {t.name: t for t in ALL_ANT_TYPES}
