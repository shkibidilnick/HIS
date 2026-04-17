"""Boolean derivatives."""
from __future__ import annotations

from itertools import combinations, product
from typing import Dict, List, Sequence, Tuple

from lab2_sem4.models import BitTuple, DerivativeResult, TruthTableRow


class BooleanDerivativeAnalyzer:
    def build_for_order(
        self,
        variables: Sequence[str],
        truth_table: Sequence[TruthTableRow],
        order: int,
    ) -> Tuple[DerivativeResult, ...]:
        if order < 1 or order > len(variables):
            return tuple()
        value_map = {tuple(row.assignment[variable] for variable in variables): row.value for row in truth_table}
        results: List[DerivativeResult] = []
        for selected_variables in combinations(variables, order):
            results.append(self._build_derivative(selected_variables, variables, value_map))
        return tuple(results)

    def _build_derivative(
        self,
        selected_variables: Tuple[str, ...],
        variables: Sequence[str],
        value_map: Dict[BitTuple, int],
    ) -> DerivativeResult:
        free_variables = tuple(variable for variable in variables if variable not in selected_variables)
        derivative_values: Dict[BitTuple, int] = {}
        for free_bits in product((0, 1), repeat=len(free_variables)):
            derivative_values[free_bits] = self._calculate_xor_sum(
                selected_variables,
                free_variables,
                free_bits,
                variables,
                value_map,
            )
        expression = self._build_expression(free_variables, derivative_values)
        return DerivativeResult(variables=selected_variables, values=derivative_values, expression=expression)

    @staticmethod
    def _calculate_xor_sum(
        selected_variables: Tuple[str, ...],
        free_variables: Tuple[str, ...],
        free_bits: BitTuple,
        variables: Sequence[str],
        value_map: Dict[BitTuple, int],
    ) -> int:
        result = 0
        for selected_bits in product((0, 1), repeat=len(selected_variables)):
            assignment = {name: bit for name, bit in zip(free_variables, free_bits)}
            assignment.update({name: bit for name, bit in zip(selected_variables, selected_bits)})
            ordered_bits = tuple(assignment[variable] for variable in variables)
            result ^= value_map[ordered_bits]
        return result

    def _build_expression(self, variables: Sequence[str], derivative_values: Dict[BitTuple, int]) -> str:
        if not variables:
            only_value = next(iter(derivative_values.values())) if derivative_values else 0
            return str(only_value)
        minterms = []
        for bits, value in derivative_values.items():
            if value == 0:
                continue
            minterms.append(self._bits_to_minterm(variables, bits))
        return ' ∨ '.join(minterms) if minterms else '0'

    @staticmethod
    def _bits_to_minterm(variables: Sequence[str], bits: BitTuple) -> str:
        literals = []
        for variable, bit in zip(variables, bits):
            literals.append(variable if bit == 1 else f'¬{variable}')
        return f"({' ∧ '.join(literals)})"
