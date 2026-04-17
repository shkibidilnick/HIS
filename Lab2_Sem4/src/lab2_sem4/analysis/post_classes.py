"""Post class analysis."""
from __future__ import annotations

from typing import Sequence

from lab2_sem4.models import PostClasses, TruthTableRow


class PostClassAnalyzer:
    def analyze(self, truth_table: Sequence[TruthTableRow]) -> PostClasses:
        preserves_zero = truth_table[0].value == 0
        preserves_one = truth_table[-1].value == 1
        self_dual = self._is_self_dual(truth_table)
        monotonic = self._is_monotonic(truth_table)
        linear = False
        return PostClasses(
            preserves_zero=preserves_zero,
            preserves_one=preserves_one,
            self_dual=self_dual,
            monotonic=monotonic,
            linear=linear,
        )

    @staticmethod
    def _is_self_dual(truth_table: Sequence[TruthTableRow]) -> bool:
        values = [row.value for row in truth_table]
        last_index = len(values) - 1
        return all(values[index] != values[last_index - index] for index in range(len(values)))

    @staticmethod
    def _is_monotonic(truth_table: Sequence[TruthTableRow]) -> bool:
        for left_row in truth_table:
            left_bits = tuple(left_row.assignment.values())
            for right_row in truth_table:
                right_bits = tuple(right_row.assignment.values())
                if PostClassAnalyzer._less_or_equal(left_bits, right_bits):
                    if left_row.value > right_row.value:
                        return False
        return True

    @staticmethod
    def _less_or_equal(left_bits: Sequence[int], right_bits: Sequence[int]) -> bool:
        return all(left_bit <= right_bit for left_bit, right_bit in zip(left_bits, right_bits))
