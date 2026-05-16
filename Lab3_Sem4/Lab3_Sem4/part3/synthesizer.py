"""
Синтез двоичного счётчика накапливающего типа на 8 внутренних состояний.

Вариант 1.
    Базис: НЕ, И, ИЛИ
    Память: Т-триггеры (3 шт.)
    Вход:  V — сигнал инкремента (V=1 → счёт +1; V=0 → состояние не меняется)
    Состояние: q3 q2 q1 (q3 — старший разряд), значения 0..7
    При V=1 в состоянии 7 происходит обнуление (переход в 0).

Методика синтеза цифрового автомата (канонический метод):
  1. Определить число триггеров: n = log2(8) = 3.
  2. Построить таблицу переходов (q3*, q2*, q1*, V) -> (q3, q2, q1).
  3. Построить таблицу возбуждения: h_i = q_i* XOR q_i
     (Т-триггер переключается ⇔ его h=1).
  4. Минимизировать функции h_i по картам Карно.
  5. Перейти от формул к схеме.
"""

from itertools import product

from karnaugh_map import KarnaughMap, Minimizer


N_TRIGGERS = 3                 # 2^3 = 8 состояний
MAX_STATE = (1 << N_TRIGGERS) - 1   # = 7

# Имена переменных: q3* — самый старший, потом q2*, q1*, потом V
EXCITATION_VARS = ('q3*', 'q2*', 'q1*', 'V')
TRIGGER_OUTPUTS = ('h3', 'h2', 'h1')   # порядок от старшего к младшему


def next_state(q3_prev, q2_prev, q1_prev, v):
    """
    Логика перехода накапливающего счётчика:
      V=0 → состояние не меняется
      V=1 → состояние увеличивается на 1 по модулю 8
    """
    state_prev = (q3_prev << 2) | (q2_prev << 1) | q1_prev
    if v == 0:
        state_next = state_prev
    else:
        state_next = (state_prev + 1) & MAX_STATE
    q3 = (state_next >> 2) & 1
    q2 = (state_next >> 1) & 1
    q1 = state_next & 1
    return q3, q2, q1


def build_transition_table():
    """
    Возвращает список строк вида
      (q3*, q2*, q1*, V, q3, q2, q1, h3, h2, h1)
    Т-триггер переключается ⇔ q_i* != q_i.
    """
    table = []
    for q3p, q2p, q1p, v in product((0, 1), repeat=4):
        q3, q2, q1 = next_state(q3p, q2p, q1p, v)
        h3 = q3p ^ q3
        h2 = q2p ^ q2
        h1 = q1p ^ q1
        table.append((q3p, q2p, q1p, v, q3, q2, q1, h3, h2, h1))
    return table


def format_transition_table(table):
    header = (
        "№  | q3* q2* q1* V | q3 q2 q1 | h3 h2 h1\n"
        "---+---------------+----------+---------"
    )
    lines = [header]
    for i, row in enumerate(table):
        q3p, q2p, q1p, v, q3, q2, q1, h3, h2, h1 = row
        lines.append(
            f"{i:>2} |  {q3p}   {q2p}   {q1p}   {v}  | "
            f" {q3}  {q2}  {q1}  |  {h3}  {h2}  {h1}"
        )
    return "\n".join(lines)


def build_karnaugh_for_h(table, h_index):
    """
    Карта Карно функции h_k(q3*, q2*, q1*, V).
    В таблице h_k находится по индексу 7+h_index, где h_index в {0,1,2}
    соответствует h3, h2, h1.
    """
    values = {}
    for row in table:
        key = row[:4]    # (q3*, q2*, q1*, V)
        values[key] = row[7 + h_index]
    return KarnaughMap(n_vars=4, var_names=list(EXCITATION_VARS), values=values)


class CounterSynthesizer:
    """
    Координирует синтез накапливающего счётчика на 8 состояний.
    """

    def __init__(self):
        self.table = build_transition_table()
        self._results = {}   # name -> (cover, expr)

    def run(self):
        report = [
            self._header(),
            self._design_section(),
            self._transition_table_section(),
            self._minimization_section(),
            self._verification_section(),
            self._schema_section(),
        ]
        return "\n\n".join(report)

    @staticmethod
    def _header():
        return (
            "=" * 70 + "\n"
            "ЛАБОРАТОРНАЯ РАБОТА 3 — ЧАСТЬ 3, ВАРИАНТ 1\n"
            "Синтез двоичного счётчика накапливающего типа\n"
            "на 8 внутренних состояний в базисе НЕ, И, ИЛИ и Т-триггер\n"
            + "=" * 70
        )

    @staticmethod
    def _design_section():
        return (
            "1. ИСХОДНЫЕ ДАННЫЕ И ВЫБОР ПАРАМЕТРОВ АВТОМАТА\n"
            "  Тип автомата: Мура (выход зависит только от состояния).\n"
            "  Число состояний: 8 → число триггеров n = log2(8) = 3.\n"
            "  Элементы памяти: Т-триггеры q3, q2, q1.\n"
            "  Входной сигнал: V (1 = инкремент, 0 = удержание).\n"
            "  Базис комбинационной части: НЕ, И, ИЛИ."
        )

    def _transition_table_section(self):
        return (
            "2. ТАБЛИЦА ПЕРЕХОДОВ И ТАБЛИЦА ВОЗБУЖДЕНИЯ\n"
            "Т-триггер переключается тогда и только тогда, когда\n"
            "состояние данного разряда изменилось: h_i = q_i* XOR q_i.\n\n"
            + format_transition_table(self.table)
        )

    def _minimization_section(self):
        lines = ["3. МИНИМИЗАЦИЯ ФУНКЦИЙ ВОЗБУЖДЕНИЯ ПО КАРТАМ КАРНО"]
        for idx, name in enumerate(TRIGGER_OUTPUTS):
            kmap = build_karnaugh_for_h(self.table, idx)
            cover, expr = Minimizer(kmap).minimize_dnf()
            self._results[name] = (cover, expr)
            lines.append("")
            lines.append(kmap.render(name))
            lines.append(f"Тупиковая ДНФ: {name} = {expr}")
        return "\n".join(lines)

    def _verification_section(self):
        lines = [
            "4. ВЕРИФИКАЦИЯ: эмуляция счётчика по полученным формулам",
            "Старт: 000, V=1. Ожидаемая последовательность: 0,1,2,...,7,0,...",
            "",
            "Такт | q3* q2* q1* | h3 h2 h1 | q3 q2 q1 | dec"
        ]
        state = (0, 0, 0)
        for tact in range(10):
            q3p, q2p, q1p = state
            v = 1
            # Вычисляем h_i по полученным минимизированным формулам
            h_vals = []
            for name in TRIGGER_OUTPUTS:
                cover, _ = self._results[name]
                h_vals.append(self._evaluate(cover, (q3p, q2p, q1p, v)))
            h3, h2, h1 = h_vals
            # Применяем переключение
            q3 = q3p ^ h3
            q2 = q2p ^ h2
            q1 = q1p ^ h1
            dec = (q3 << 2) | (q2 << 1) | q1
            lines.append(
                f" {tact:>2}  |  {q3p}   {q2p}   {q1p}  |  "
                f"{h3}  {h2}  {h1}  |  {q3}  {q2}  {q1}  | {dec}"
            )
            state = (q3, q2, q1)
        return "\n".join(lines)

    @staticmethod
    def _evaluate(cover, x_vals):
        for impl in cover:
            if all(p == '-' or p == v for p, v in zip(impl, x_vals)):
                return 1
        return 0

    def _schema_section(self):
        h3_expr = self._results['h3'][1]
        h2_expr = self._results['h2'][1]
        h1_expr = self._results['h1'][1]
        return (
            "5. ОПИСАНИЕ СХЕМЫ ДЛЯ LOGISIM\n"
            "Полученные функции возбуждения:\n"
            f"  h3 = {h3_expr}\n"
            f"  h2 = {h2_expr}\n"
            f"  h1 = {h1_expr}\n\n"
            "Структурная схема:\n"
            "  - 3 Т-триггера: T1 (q1), T2 (q2), T3 (q3).\n"
            "  - Общий тактовый сигнал Clock подключается ко всем триггерам.\n"
            "  - Вход V управляет инкрементом (см. примечание).\n"
            "  - Комбинационная часть формирует h1, h2, h3 из выходов\n"
            "    предыдущего такта (q1*, q2*, q3*) и V:\n"
            "       h1 — напрямую с V (буфер или провод)\n"
            "       h2 — И(q1*, V)\n"
            "       h3 — И(q2*, q1*, V)\n"
            "  - Выходы триггеров q1, q2, q3 разводятся:\n"
            "     • на внешние Output-пины (показывают состояние),\n"
            "     • обратно на комбинационную схему (q1*=q1, q2*=q2, q3*=q3 \n"
            "       в момент перед фронтом такта).\n\n"
            "Сборка в Logisim:\n"
            "  1. Memory → T Flip-Flop ×3.\n"
            "  2. Подключить общий Clock ко всем тактовым входам.\n"
            "  3. Сигнал V подать как вход, при V=1 счётчик считает,\n"
            "     при V=0 удерживает состояние.\n"
            "  4. Собрать комбинационную часть из элементов AND из Gates\n"
            "     (для h3 нужен AND на 3 входа).\n"
            "  5. Подключить выходы каждого T-триггера к Output Pin (q3,q2,q1)\n"
            "     и обратно в комбинационную схему.\n"
            "  6. Проверить запуском (Simulate → Ticks Enabled): счётчик\n"
            "     должен последовательно выдавать 000,001,010,...,111,000."
        )


def main():
    synth = CounterSynthesizer()
    print(synth.run())


if __name__ == "__main__":
    main()
