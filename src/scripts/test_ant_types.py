import sys
import os

# garantir que o pacote `src` está no path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from entities.ant_types import ALL_ANT_TYPES
from entities.ant import Ant

def main():
    for t in ALL_ANT_TYPES:
        a = Ant((0, 0), t)
        print(a, "dps=", a.dps, "speed=", a.speed, "special=", a.special_effect)

if __name__ == '__main__':
    main()
