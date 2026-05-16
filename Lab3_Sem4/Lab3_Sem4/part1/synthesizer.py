"""
Синтез одноразрядного двоичного сумматора на 3 входа (ОДС-3)
с представлением выходных функций в СКНФ.

Вариант 3:
    Входы:  x1, x2, x3 (два слагаемых и перенос с младшего разряда)
    Выходы: S (бит суммы), P (перенос в старший разряд)
"""

from itertools import product

from karnaugh_map import KarnaughMap, Minimizer


INPUT_NAMES = ('x1', 'x2', 'x3')
OUTPUT_NAMES = ('S', 'P')


def build_truth_table():
    """
    Возвращает список кортежей (x1, x2, x3, S, P) для всех 8 наборов.
    S = младший бит суммы x1+x2+x3
    P = старший бит суммы (перенос)
    """
    table = []
    for x1, x2, x3 in product((0, 1), repeat=3):
        total = x1 + x2 + x3
        s_bit = total & 1
        p_bit = (total >> 1) & 1
        table.append((x1, x2, x3, s_bit, p_bit))
    return table


def format_truth_table(table):
    lines = ["№ | x1 x2 x3 | S P", "--+----------+----"]
    for i, (x1, x2, x3, s, p) in enumerate(table):
        lines.append(f"{i} |  {x1}  {x2}  {x3} | {s} {p}")
    return "\n".join(lines)


def sknf_expression(table, out_idx, names=INPUT_NAMES):
    """Запись функции в СКНФ — произведение макстермов по нулевым наборам."""
    maxterms = []
    for row in table:
        x_vals = row[:3]
        f = row[3 + out_idx]
        if f == 0:
            parts = [name if v == 0 else f"¬{name}"
                     for v, name in zip(x_vals, names)]
            maxterms.append("(" + "∨".join(parts) + ")")
    return "·".join(maxterms) if maxterms else "1"


def build_karnaugh_for(table, out_idx):
    """Строит карту Карно для одного из выходов (S или P)."""
    values = {}
    for row in table:
        x_vals = row[:3]
        values[x_vals] = row[3 + out_idx]
    return KarnaughMap(n_vars=3, var_names=list(INPUT_NAMES), values=values)


class OdsThreeSynthesizer:
    """
    Координирует синтез ОДС-3 в СКНФ:
    1) таблица истинности
    2) СКНФ S и P
    3) карты Карно и минимизация по нулям
    4) описание схемы
    """

    def __init__(self):
        self.table = build_truth_table()

    def run(self):
        report = []
        report.append(self._header())
        report.append(self._truth_table_section())
        report.append(self._sknf_section())
        report.append(self._minimization_section())
        report.append(self._equipment_section())
        report.append(self._scaling_section())
        return "\n\n".join(report)

    @staticmethod
    def _header():
        return (
            "=" * 70 + "\n"
            "ЛАБОРАТОРНАЯ РАБОТА 3 — ЧАСТЬ 1, ВАРИАНТ 3\n"
            "Синтез ОДС-3 (одноразрядный двоичный сумматор на 3 входа)\n"
            "с представлением выходных функций в СКНФ\n"
            + "=" * 70
        )

    def _truth_table_section(self):
        return (
            "1. ТАБЛИЦА ИСТИННОСТИ\n"
            "Входы:  x1, x2 — слагаемые, x3 — перенос из младшего разряда\n"
            "Выходы: S — сумма в разряде, P — перенос в старший разряд\n\n"
            + format_truth_table(self.table)
        )

    def _sknf_section(self):
        s_expr = sknf_expression(self.table, out_idx=0)
        p_expr = sknf_expression(self.table, out_idx=1)
        return (
            "2. ЗАПИСЬ ФУНКЦИЙ В СКНФ\n"
            "СКНФ строится по наборам, где функция равна 0:\n"
            "переменная x=1 входит в макстерм с инверсией, x=0 — без.\n\n"
            f"S = {s_expr}\n\n"
            f"P = {p_expr}"
        )

    def _minimization_section(self):
        lines = ["3. МИНИМИЗАЦИЯ ПО КАРТАМ КАРНО (минимизация по нулям → КНФ)"]
        self._minimized = {}

        for idx, name in enumerate(OUTPUT_NAMES):
            kmap = build_karnaugh_for(self.table, idx)
            cover, expr = Minimizer(kmap).minimize_knf()
            self._minimized[name] = (cover, expr)

            lines.append("")
            lines.append(kmap.render(name))
            lines.append(f"Тупиковая КНФ: {name} = {expr}")
            if not cover:
                lines.append("(не минимизируется — нули не группируются)")
            else:
                lines.append(f"Простых импликант-макстермов: {len(cover)}")

        return "\n".join(lines)

    def _equipment_section(self):
        lines = ["4. СОСТАВ ОБОРУДОВАНИЯ (1 разряд)"]
        s_cover, _ = self._minimized['S']
        p_cover, _ = self._minimized['P']

        not_count = len(INPUT_NAMES)
        or_groups = {}
        for cover in (s_cover, p_cover):
            for impl in cover:
                k = sum(1 for v in impl if v != '-')
                if k >= 2:
                    or_groups[k] = or_groups.get(k, 0) + 1
        and_groups = {len(s_cover): 1, len(p_cover): 1}

        lines.append(f"  - элементов НЕ: {not_count} (по одному на каждую переменную)")
        for k in sorted(or_groups):
            lines.append(f"  - элементов ИЛИ на {k} входа: {or_groups[k]}")
        for k in sorted(and_groups):
            lines.append(f"  - элементов И на {k} входов: {and_groups[k]}")
        return "\n".join(lines)

    def _scaling_section(self):
        return (
            "5. МАСШТАБИРОВАНИЕ ДО 8 РАЗРЯДОВ\n"
            "8-разрядный сумматор = каскад из 8 одинаковых блоков ОДС-3.\n\n"
            "Соединения:\n"
            "  Разряд i:  x1 ← A[i],  x2 ← B[i],  x3 ← P_{i-1}\n"
            "  Для разряда 0:  x3 = Cin (внешний перенос, обычно 0)\n"
            "  Перенос P старшего разряда = Cout (переполнение).\n\n"
            "В Logisim:\n"
            "  1. Подсхема ODS3 с входами x1, x2, x3 и выходами S, P.\n"
            "  2. Главная схема: 8 копий ODS3, входы A и B по 8 бит\n"
            "     разделяются Splitter'ами на отдельные линии.\n"
            "  3. Выходы S0..S7 собираются Splitter'ом в шину Sum.\n"
            "  4. Демонстрация 8 + 6 = 14:\n"
            "       A = 00001000, B = 00000110 → Sum = 00001110, Cout = 0"
        )


def main():
    synth = OdsThreeSynthesizer()
    print(synth.run())


if __name__ == "__main__":
    main()
