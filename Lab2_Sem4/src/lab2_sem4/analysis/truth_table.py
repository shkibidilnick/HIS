"""Truth table generation."""
from __future__ import annotations

from itertools import product
from typing import List, Tuple

from lab2_sem4.core.expression import BooleanExpression
from lab2_sem4.models import TruthTableRow


class TruthTableBuilder:
    def build(self, expression: BooleanExpression) -> Tuple[TruthTableRow, ...]:
        rows: List[TruthTableRow] = []
        for bits in product((0, 1), repeat=len(expression.variables)):
            assignment = dict(zip(expression.variables, bits))
            index = self._bits_to_index(bits)
            value = expression.evaluate(assignment)
            rows.append(TruthTableRow(index=index, assignment=assignment, value=value))
        return tuple(rows)

    @staticmethod
    def _bits_to_index(bits: Tuple[int, ...]) -> int:
        result = 0
        for bit in bits:
            result = (result << 1) | bit
        return result
