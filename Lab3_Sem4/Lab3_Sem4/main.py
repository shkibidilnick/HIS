"""
Лабораторная работа 3, Семестр 4.
Точка входа с меню выбора части.

Варианты:
    Часть 1 — Вариант 3 (ОДС-3 в СКНФ)
    Часть 2 — Вариант А, смещение г (8421 BCD + 5)
    Часть 3 — Вариант 1 (суммирующий счётчик на 8 состояний)
"""

import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from part1 import main as part1_main
from part2 import main as part2_main
from part3 import main as part3_main


PARTS = {
    "1": ("Часть 1 — ОДС-3 в СКНФ (вариант 3)", part1_main.run),
    "2": ("Часть 2 — преобразователь BCD+5 (вариант А, смещение г)", part2_main.run),
    "3": ("Часть 3 — счётчик на 8 состояний (вариант 1)", part3_main.run),
    "0": ("Выйти", None),
}


def show_menu():
    print()
    print("=" * 70)
    print("ЛАБОРАТОРНАЯ РАБОТА 3 — выбор части")
    print("=" * 70)
    for key in ("1", "2", "3", "0"):
        title, _ = PARTS[key]
        print(f"  {key}. {title}")
    print()


def main():
    while True:
        show_menu()
        choice = input("  Выбор: ").strip()
        if choice not in PARTS:
            print("  Неверный выбор, попробуйте ещё раз.")
            continue
        if choice == "0":
            print("  Выход.")
            return
        _, runner = PARTS[choice]
        print()
        runner()
        print()
        input("  Нажмите Enter, чтобы вернуться в меню...")


if __name__ == "__main__":
    main()
