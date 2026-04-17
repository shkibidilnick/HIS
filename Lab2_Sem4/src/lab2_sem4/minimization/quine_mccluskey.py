"""Quine-McCluskey style exact minimization."""
from __future__ import annotations

from typing import Callable, Sequence, Tuple

from lab2_sem4.minimization.common import (
    ExactCoverSelector,
    PrimeImplicantFinder,
    build_coverage_table,
    index_to_mask,
)
from lab2_sem4.models import Mask, MinimizationResult


class ExactMinimizer:
    def __init__(self, formatter: Callable[[Mask, Sequence[str]], str], joiner: str) -> None:
        self._formatter = formatter
        self._joiner = joiner
        self._prime_implicant_finder = PrimeImplicantFinder()
        self._cover_selector = ExactCoverSelector()

    def minimize(self, indices: Sequence[int], variables: Sequence[str]) -> MinimizationResult:
        if not indices:
            empty_expression = '0' if self._joiner == ' ∨ ' else '1'
            return MinimizationResult(
                prime_implicants=tuple(),
                selected_implicants=tuple(),
                stages=tuple(),
                coverage_table=build_coverage_table(tuple(), tuple(), variables, self._formatter),
                expression=empty_expression,
            )
        masks = [index_to_mask(index, len(variables)) for index in indices]
        prime_implicants, stages = self._prime_implicant_finder.build_stages(masks)
        selected = self._cover_selector.select(prime_implicants, indices, variables)
        coverage_table = build_coverage_table(prime_implicants, indices, variables, self._formatter)
        ordered_selected = tuple(sorted(selected, key=lambda mask: (sum(1 for bit in mask if bit is not None), self._formatter(mask, variables))))
        expression_parts = [self._formatter(mask, variables) for mask in ordered_selected]
        expression = self._joiner.join(expression_parts) if expression_parts else ('0' if self._joiner == ' ∨ ' else '1')
        return MinimizationResult(
            prime_implicants=prime_implicants,
            selected_implicants=selected,
            stages=stages,
            coverage_table=coverage_table,
            expression=expression,
        )
