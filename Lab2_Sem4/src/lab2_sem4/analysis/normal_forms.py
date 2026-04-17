"""Canonical normal forms."""
from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple

from lab2_sem4.models import NormalForms, TruthTableRow


class NormalFormBuilder:
    def build(self, variables: Sequence[str], truth_table: Sequence[TruthTableRow]) -> NormalForms:
        one_rows = [row for row in truth_table if row.value == 1]
        zero_rows = [row for row in truth_table if row.value == 0]
        sdnf_terms = [self._build_minterm(variables, row) for row in one_rows]
        sknf_terms = [self._build_maxterm(variables, row) for row in zero_rows]
        sdnf = ' ∨ '.join(sdnf_terms) if sdnf_terms else '0'
        sknf = ' ∧ '.join(sknf_terms) if sknf_terms else '1'
        sdnf_numeric = self._numeric_form('Σ', (row.index for row in one_rows))
        sknf_numeric = self._numeric_form('Π', (row.index for row in zero_rows))
        index_form = ''.join(str(row.value) for row in truth_table)
        return NormalForms(
            sdnf=sdnf,
            sknf=sknf,
            sdnf_numeric=sdnf_numeric,
            sknf_numeric=sknf_numeric,
            index_form=index_form,
        )

    @staticmethod
    def _build_minterm(variables: Sequence[str], row: TruthTableRow) -> str:
        literals = []
        for variable in variables:
            literals.append(variable if row.assignment[variable] == 1 else f'¬{variable}')
        return f"({' ∧ '.join(literals)})"

    @staticmethod
    def _build_maxterm(variables: Sequence[str], row: TruthTableRow) -> str:
        literals = []
        for variable in variables:
            literals.append(variable if row.assignment[variable] == 0 else f'¬{variable}')
        return f"({' ∨ '.join(literals)})"

    @staticmethod
    def _numeric_form(symbol: str, indices: Iterable[int]) -> str:
        joined = ', '.join(str(index) for index in indices)
        return f'{symbol}({joined})'
