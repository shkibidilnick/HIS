"""
Модуль построения и минимизации логических функций
методом карты Карно для функций до 4 переменных.

Реализует табличный метод минимизации:
1. Построение карты Карно из таблицы истинности
2. Поиск всех допустимых прямоугольных областей (импликант)
3. Выбор минимального покрытия

Принципы:
- KISS: алгоритм максимально прямой, без оптимизаций
- DRY: одна реализация для ДНФ и КНФ (через параметр target_value)
- SRP: класс отвечает только за карту Карно и минимизацию
"""

from itertools import combinations, product


# Порядок переменных в строках/столбцах карты Карно (код Грея)
GRAY_2 = [(0, 0), (0, 1), (1, 1), (1, 0)]
GRAY_1 = [(0,), (1,)]


class KarnaughMap:
    """
    Карта Карно для функции от n переменных (n = 3 или 4).
    Внутри хранит значения функции по наборам аргументов.

    Значения ячеек:
        0   - функция равна 0
        1   - функция равна 1
        None - don't care (избыточный набор)
    """

    def __init__(self, n_vars, var_names, values):
        """
        :param n_vars: количество переменных (3 или 4)
        :param var_names: список имён переменных, var_names[0] - старшая
        :param values: dict {tuple_of_bits: 0|1|None}
        """
        if n_vars not in (3, 4):
            raise ValueError("Поддерживаются только 3 или 4 переменных")
        if len(var_names) != n_vars:
            raise ValueError("Количество имён не совпадает с количеством переменных")

        self.n_vars = n_vars
        self.var_names = var_names
        self.values = values
        self._row_codes, self._col_codes = self._gray_codes()

    def _gray_codes(self):
        """Возвращает (row_codes, col_codes) для карты с разбиением переменных."""
        if self.n_vars == 3:
            # 1 переменная в строках, 2 в столбцах
            return GRAY_1, GRAY_2
        # n_vars == 4: 2 переменных в строках, 2 в столбцах
        return GRAY_2, GRAY_2

    def _split_assignment(self, assignment):
        """Разбивает набор на (row_part, col_part) для размещения на карте."""
        n_rows_vars = len(self._row_codes[0])
        return assignment[:n_rows_vars], assignment[n_rows_vars:]

    def render(self, label):
        """Возвращает строковое представление карты Карно."""
        lines = []
        row_vars = " ".join(self.var_names[:len(self._row_codes[0])])
        col_vars = " ".join(self.var_names[len(self._row_codes[0]):])
        lines.append(f"Карта Карно для {label}({', '.join(self.var_names)}):")
        lines.append(f"  строки: {row_vars}, столбцы: {col_vars}")

        # Заголовок
        header = "     " + " ".join("".join(str(b) for b in c) for c in self._col_codes)
        lines.append(header)

        for r in self._row_codes:
            r_str = "".join(str(b) for b in r)
            cells = []
            for c in self._col_codes:
                v = self.values[r + c]
                cells.append("X" if v is None else str(v))
            lines.append(f"  {r_str}  " + "  ".join(cells))

        return "\n".join(lines)


class Minimizer:
    """
    Минимизирует функцию по карте Карно через перебор прямоугольных
    импликант (методом полного перебора простых импликант).

    Алгоритм:
    1. Найти все максимальные прямоугольные области целевых клеток
       (учитывая заворот карты Карно).
    2. Из этих простых импликант выбрать минимальное покрытие
       обязательных клеток (без don't care).
    """

    def __init__(self, karnaugh_map):
        self.kmap = karnaugh_map
        self.n = karnaugh_map.n_vars

    def minimize_dnf(self):
        """
        Минимизация по единицам (для ДНФ).
        Возвращает (список импликант, текстовое выражение).
        Каждая импликанта — кортеж из n значений {0, 1, '-'}.
        """
        return self._minimize(target=1, dont_care=None, mode='dnf')

    def minimize_knf(self):
        """Минимизация по нулям (для КНФ)."""
        return self._minimize(target=0, dont_care=None, mode='knf')

    def _minimize(self, target, dont_care, mode):
        # Обязательные наборы (где функция = target)
        must_cover = [a for a, v in self.kmap.values.items() if v == target]

        # Допустимые наборы (target + don't care)
        allowed = [a for a, v in self.kmap.values.items()
                   if v == target or v is None]

        if not must_cover:
            const = "1" if mode == 'knf' else "0"
            return [], const

        prime_implicants = self._find_prime_implicants(allowed, must_cover)
        cover = self._find_minimal_cover(prime_implicants, must_cover)
        expression = self._render_expression(cover, mode)
        return cover, expression

    def _find_prime_implicants(self, allowed_set, must_cover_set):
        """
        Находит все простые (максимальные) импликанты.
        Импликанта — это прямоугольный блок размера 2^k клеток,
        в котором все клетки принадлежат allowed_set.
        """
        allowed = set(allowed_set)
        must = set(must_cover_set)

        # Перебираем размеры блока 2^k от наибольшего к наименьшему
        # Блок задаётся выбором подмножества "фиксированных" позиций
        # и значениями на них. Остальные позиции — свободные ("-").

        all_implicants = []
        for fixed_mask in range(2 ** self.n):
            free_positions = [i for i in range(self.n)
                              if not (fixed_mask >> i) & 1]
            fixed_positions = [i for i in range(self.n)
                               if (fixed_mask >> i) & 1]

            # Перебор значений на фиксированных позициях
            for fixed_vals in product([0, 1], repeat=len(fixed_positions)):
                impl = ['-'] * self.n
                for pos, val in zip(fixed_positions, fixed_vals):
                    impl[pos] = val
                impl_tuple = tuple(impl)

                # Получаем все клетки, покрываемые этой импликантой
                cells = self._cells_of(impl_tuple)

                # Все клетки должны быть allowed, и хотя бы одна — обязательная
                if all(c in allowed for c in cells) and any(c in must for c in cells):
                    all_implicants.append(impl_tuple)

        # Оставляем только простые (не поглощаемые другими) импликанты
        primes = []
        for impl in all_implicants:
            if not any(self._strictly_covers(other, impl)
                       for other in all_implicants if other != impl):
                primes.append(impl)

        return primes

    def _cells_of(self, impl):
        """Возвращает множество клеток, которые покрывает импликанта."""
        free_positions = [i for i, v in enumerate(impl) if v == '-']
        cells = []
        for free_vals in product([0, 1], repeat=len(free_positions)):
            cell = list(impl)
            for pos, val in zip(free_positions, free_vals):
                cell[pos] = val
            cells.append(tuple(cell))
        return cells

    @staticmethod
    def _strictly_covers(big, small):
        """
        big строго покрывает small, если множество клеток small
        является собственным подмножеством множества клеток big.
        Это эквивалентно: big имеет больше '-' и совпадает с small
        во всех фиксированных позициях big.
        """
        if big == small:
            return False
        for b, s in zip(big, small):
            if b != '-' and b != s:
                return False
        return True

    def _find_minimal_cover(self, primes, must_cover):
        """Поиск минимального набора простых импликант, покрывающего must_cover."""
        must_set = set(must_cover)
        n = len(primes)

        # Сначала найдём существенные импликанты (покрывающие клетки,
        # которые больше никто не покрывает)
        essential = []
        remaining = set(must_set)

        for cell in must_set:
            covering = [p for p in primes if cell in self._cells_of(p)]
            if len(covering) == 1 and covering[0] not in essential:
                essential.append(covering[0])

        for e in essential:
            remaining -= set(self._cells_of(e))

        if not remaining:
            return essential

        # Для оставшихся клеток — перебор минимального покрытия
        rest_primes = [p for p in primes if p not in essential]
        for size in range(1, len(rest_primes) + 1):
            for combo in combinations(rest_primes, size):
                covered = set()
                for p in combo:
                    covered.update(self._cells_of(p))
                if remaining.issubset(covered):
                    return essential + list(combo)

        return essential + rest_primes

    def _render_expression(self, cover, mode):
        if not cover:
            return "1" if mode == 'knf' else "0"
        if mode == 'dnf':
            terms = [self._impl_to_conjunction(impl) for impl in cover]
            return " ∨ ".join(terms)
        terms = [self._impl_to_disjunction(impl) for impl in cover]
        return " · ".join(terms)

    def _impl_to_conjunction(self, impl):
        """Импликанта → конъюнкция (для ДНФ): val=1 → x, val=0 → ¬x."""
        parts = []
        for v, name in zip(impl, self.kmap.var_names):
            if v == '-':
                continue
            parts.append(name if v == 1 else f"¬{name}")
        if not parts:
            return "1"
        return parts[0] if len(parts) == 1 else "(" + "·".join(parts) + ")"

    def _impl_to_disjunction(self, impl):
        """Импликанта → дизъюнкция (для КНФ): val=0 → x, val=1 → ¬x."""
        parts = []
        for v, name in zip(impl, self.kmap.var_names):
            if v == '-':
                continue
            parts.append(name if v == 0 else f"¬{name}")
        if not parts:
            return "0"
        return parts[0] if len(parts) == 1 else "(" + "∨".join(parts) + ")"
