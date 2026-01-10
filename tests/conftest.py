import os
import sys

# Ensure src is on sys.path for tests
BASE_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.join(os.path.dirname(BASE_DIR), "src")
if SRC_DIR not in sys.path:
    # append instead of insert to avoid importing modules in src/scripts
    # that start with `test_` before pytest collects test files
    sys.path.append(SRC_DIR)
