"""Karnaugh map builder for 1..5 variables."""
from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

from lab2_sem4.constants import MAX_KARNAUGH_VARIABLE_COUNT
from lab2_sem4.minimization.common import mask_to_cnf_clause, mask_to_dnf_term
from lab2_sem4.minimization.quine_mccluskey import ExactMinimizer
from lab2_sem4.models import KarnaughMapResult, TruthTableRow

_GRAY_ORDERS = {
    0: ('',),
    1: ('0', '1'),
    2: ('00', '01', '11', '10'),
    3: ('000', '001', '011', '010', '110', '111', '101', '100'),
}


class KarnaughMapBuilder:
    def __init__(self) -> None:
        self._dnf_minimizer = ExactMinimizer(mask_to_dnf_term, ' ∨ ')
        self._cnf_minimizer = ExactMinimizer(mask_to_cnf_clause, ' ∧ ')

    def build(
        self,
        variables: Sequence[str],
        truth_table: Sequence[TruthTableRow],
    ) -> Optional[KarnaughMapResult]:
        if len(variables) > MAX_KARNAUGH_VARIABLE_COUNT:
            return None

        row_variable_count = len(variables) // 2
        column_variable_count = len(variables) - row_variable_count

        row_labels = _GRAY_ORDERS[row_variable_count]
        column_labels = _GRAY_ORDERS[column_variable_count]

        value_map = {
            ''.join(str(row.assignment[variable]) for variable in variables): row.value
            for row in truth_table
        }

        grid: List[Tuple[int, ...]] = []
        for row_label in row_labels:
            row_values = []
            for column_label in column_labels:
                key = row_label + column_label
                row_values.append(value_map[key])
            grid.append(tuple(row_values))

        one_indices = [row.index for row in truth_table if row.value == 1]
        zero_indices = [row.index for row in truth_table if row.value == 0]

        return KarnaughMapResult(
            variable_order=tuple(variables),
            row_labels=tuple(row_labels),
            column_labels=tuple(column_labels),
            grid=tuple(grid),
            dnf_expression=self._dnf_minimizer.minimize(one_indices, variables).expression,
            cnf_expression=self._cnf_minimizer.minimize(zero_indices, variables).expression,
        )