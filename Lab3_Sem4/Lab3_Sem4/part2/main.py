"""Точка входа: синтез преобразователя BCD → BCD+5, вариант А-г."""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from synthesizer import main as run


if __name__ == "__main__":
    run()