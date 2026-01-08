import os
import sys

# Ensure src is on sys.path for tests
BASE_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.join(os.path.dirname(BASE_DIR), "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
