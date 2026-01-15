
from src.entities.ant_types import ALL_ANT_TYPES
from src.entities.ant import Ant


def main() -> None:
    for t in ALL_ANT_TYPES:
        a = Ant((0, 0), t)
        print(a, "dps=", a.dps, "speed=", a.speed, "special=", a.special_effect)


if __name__ == "__main__":
    main()
