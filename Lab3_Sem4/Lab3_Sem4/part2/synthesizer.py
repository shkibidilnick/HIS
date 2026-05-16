"""
Синтез преобразователя тетрад десятично-двоичного кода Д8421 → Д8421+5
как устройства с не полностью определёнными функциями.

Вариант А (8421 BCD), смещение г) n=5.

    Вход:  x4 x3 x2 x1 — BCD-цифра (0..9), x4 — старший бит
    Выход: y4 y3 y2 y1 — двоичный код числа (вход + 5), y4 — старший бит
    Наборы 10..15 на входе никогда не появляются (don't care).
"""

from itertools import product

from karnaugh_map import KarnaughMap, Minimizer


N_SHIFT = 5
INPUT_NAMES = ('x4', 'x3', 'x2', 'x1')
OUTPUT_NAMES = ('y4', 'y3', 'y2', 'y1')

BCD_MAX_VALID = 9


def build_truth_table(shift=N_SHIFT):
    """
    Возвращает список кортежей (x4, x3, x2, x1, y4, y3, y2, y1),
    где y_k = None означает don't care.
    """
    table = []
    for x4, x3, x2, x1 in product((0, 1), repeat=4):
        x = (x4 << 3) | (x3 << 2) | (x2 << 1) | x1
        if x <= BCD_MAX_VALID:
            y = x + shift
            y4 = (y >> 3) & 1
            y3 = (y >> 2) & 1
            y2 = (y >> 1) & 1
            y1 = y & 1
            outs = (y4, y3, y2, y1)
        else:
            outs = (None, None, None, None)
        table.append((x4, x3, x2, x1, *outs))
    return table


def format_truth_table(table):
    lines = [
        "J  | x4 x3 x2 x1 | y4 y3 y2 y1",
        "---+-------------+------------"
    ]
    for i, row in enumerate(table):
        xs = row[:4]
        ys = row[4:]
        xs_str = "  ".join(str(b) for b in xs)
        ys_str = "  ".join("-" if y is None else str(y) for y in ys)
        lines.append(f"{i:>2} |  {xs_str}  |  {ys_str}")
    return "\n".join(lines)


def build_karnaugh_for(table, out_idx):
    """Карта Карно для одного выхода. None в значениях — don't care."""
    values = {}
    for row in table:
        x_vals = row[:4]
        values[x_vals] = row[4 + out_idx]
    return KarnaughMap(n_vars=4, var_names=list(INPUT_NAMES), values=values)


def count_literals(cover):
    """Сумма литералов во всех импликантах + операций соединения."""
    lits = sum(sum(1 for v in p if v != '-') for p in cover)
    ops = max(0, len(cover) - 1)
    return lits + ops


def evaluate_dnf(cover, x_vals):
    """Вычислить значение функции ДНФ на наборе x_vals."""
    for impl in cover:
        if all(p == '-' or p == v for p, v in zip(impl, x_vals)):
            return 1
    return 0


def evaluate_knf(cover, x_vals):
    """Вычислить значение функции КНФ на наборе x_vals.

    Макстерм = 0 на наборе, если для всех его фиксированных позиций:
      p == 0 и x == 0  (литерал = x)        → литерал = 0
      p == 1 и x == 1  (литерал = ¬x)       → литерал = 0
    То есть p == x. В этом случае весь макстерм = 0 → КНФ = 0.
    """
    for impl in cover:
        is_zero = all(p == '-' or p == v for p, v in zip(impl, x_vals))
        if is_zero:
            return 0
    return 1


class BcdPlus5Synthesizer:
    """
    Координирует синтез преобразователя BCD → BCD+5.
    Для каждого выхода выбирается более компактная форма (ДНФ или КНФ).
    """

    def __init__(self):
        self.table = build_truth_table()
        self._results = {}  # name -> (form, cover, expr)

    def run(self):
        report = [self._header(), self._truth_table_section()]
        report.append(self._minimization_section())
        report.append(self._verification_section())
        report.append(self._schema_section())
        return "\n\n".join(report)

    @staticmethod
    def _header():
        return (
            "=" * 70 + "\n"
            "ЛАБОРАТОРНАЯ РАБОТА 3 — ЧАСТЬ 2\n"
            "Вариант А (BCD 8421), смещение г) n=5\n"
            "Преобразователь тетрад Д8421 → Д8421+5\n"
            + "=" * 70
        )

    def _truth_table_section(self):
        return (
            "1. ТАБЛИЦА ИСТИННОСТИ\n"
            "Наборы 10..15 — избыточные (don't care), помечены прочерками.\n\n"
            + format_truth_table(self.table)
        )

    def _minimization_section(self):
        lines = ["2. МИНИМИЗАЦИЯ ПО КАРТАМ КАРНО С УЧЁТОМ DON'T CARE"]

        for idx, name in enumerate(OUTPUT_NAMES):
            kmap = build_karnaugh_for(self.table, idx)
            minimizer = Minimizer(kmap)
            dnf_cover, dnf_expr = minimizer.minimize_dnf()
            knf_cover, knf_expr = minimizer.minimize_knf()

            dnf_score = count_literals(dnf_cover)
            knf_score = count_literals(knf_cover)

            if dnf_score <= knf_score:
                form, cover, expr = 'ДНФ', dnf_cover, dnf_expr
            else:
                form, cover, expr = 'КНФ', knf_cover, knf_expr
            self._results[name] = (form, cover, expr)

            lines.append("")
            lines.append(kmap.render(name))
            lines.append(f"  Тупиковая ДНФ: {name} = {dnf_expr}   "
                         f"(сложность {dnf_score})")
            lines.append(f"  Тупиковая КНФ: {name} = {knf_expr}   "
                         f"(сложность {knf_score})")
            lines.append(f"  Выбрана форма: {form}")

        return "\n".join(lines)

    def _verification_section(self):
        lines = [
            "3. ВЕРИФИКАЦИЯ НА РАБОЧИХ НАБОРАХ (0..9)",
            "X  | ожидание | вычислено | OK",
            "---+----------+-----------+----"
        ]
        all_ok = True
        for row in self.table:
            xs = row[:4]
            expected = row[4:]
            if expected[0] is None:
                continue

            computed = []
            for idx, name in enumerate(OUTPUT_NAMES):
                form, cover, _ = self._results[name]
                value = (evaluate_dnf(cover, xs) if form == 'ДНФ'
                         else evaluate_knf(cover, xs))
                computed.append(value)

            ok = tuple(computed) == expected
            all_ok = all_ok and ok
            x_val = (xs[0] << 3) | (xs[1] << 2) | (xs[2] << 1) | xs[3]
            e_str = "".join(str(v) for v in expected)
            c_str = "".join(str(v) for v in computed)
            lines.append(f"{x_val:>2} |   {e_str}   |   {c_str}    | "
                         f"{'✓' if ok else '✗'}")

        lines.append("")
        lines.append("ИТОГ: " + ("все наборы верны ✓" if all_ok else "ОШИБКА ✗"))
        return "\n".join(lines)

    def _schema_section(self):
        lines = [
            "4. ОПИСАНИЕ СХЕМЫ ДЛЯ LOGISIM (без масштабирования)",
            "",
            "Финальные формулы:"
        ]
        for name in OUTPUT_NAMES:
            form, _, expr = self._results[name]
            lines.append(f"  {name} = {expr}    [{form}]")

        lines += [
            "",
            "Сборка:",
            "  Входы (1 бит):  x4 (старший), x3, x2, x1 (младший)",
            "  Выходы (1 бит): y4, y3, y2, y1",
            "",
            "  Общие инверторы НЕ выставляются один раз на каждую переменную,",
            "  их выходы переиспользуются всеми функциями.",
            "",
            "  Для каждой функции y_k:",
            "    ДНФ: каждая конъюнкция → элемент И,",
            "         все конъюнкции объединяются элементом ИЛИ.",
            "    КНФ: каждая дизъюнкция → элемент ИЛИ,",
            "         все дизъюнкции объединяются элементом И.",
            "",
            "  По заданию схема переносится в Logisim как есть (без каскада).",
        ]
        return "\n".join(lines)


def main():
    synth = BcdPlus5Synthesizer()
    print(synth.run())


if __name__ == "__main__":
    main()
