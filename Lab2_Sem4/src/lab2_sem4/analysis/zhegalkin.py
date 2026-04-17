"""Zhegalkin polynomial builder."""
from __future__ import annotations

from typing import List, Sequence, Tuple

from lab2_sem4.models import TruthTableRow


class ZhegalkinBuilder:
    def build(self, variables: Sequence[str], truth_table: Sequence[TruthTableRow]) -> Tuple[str, bool]:
        coefficients = self._build_coefficients([row.value for row in truth_table])
        terms = []
        for index, coefficient in enumerate(coefficients):
            if coefficient == 0:
                continue
            term = self._index_to_term(index, variables)
            terms.append(term)
        polynomial = ' ⊕ '.join(terms) if terms else '0'
        is_linear = self._is_linear_coefficients(coefficients)
        return polynomial, is_linear

    @staticmethod
    def _build_coefficients(values: List[int]) -> List[int]:
        coefficients = []
        current_row = values[:]
        while current_row:
            coefficients.append(current_row[0])
            current_row = [left ^ right for left, right in zip(current_row, current_row[1:])]
        return coefficients

    @staticmethod
    def _index_to_term(index: int, variables: Sequence[str]) -> str:
        if index == 0:
            return '1'
        bits = format(index, f'0{len(variables)}b')
        literals = [variable for variable, bit in zip(variables, bits) if bit == '1']
        return ''.join(literals)

    @staticmethod
    def _is_linear_coefficients(coefficients: Sequence[int]) -> bool:
        for index, coefficient in enumerate(coefficients):
            if coefficient == 0:
                continue
            if index.bit_count() > 1:
                return False
        return True
