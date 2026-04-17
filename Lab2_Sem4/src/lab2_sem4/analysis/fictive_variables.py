"""Detection of fictive variables."""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Sequence, Tuple

from lab2_sem4.models import TruthTableRow


class FictiveVariableAnalyzer:
    def find(self, variables: Sequence[str], truth_table: Sequence[TruthTableRow]) -> Tuple[str, ...]:
        fictive_variables: List[str] = []
        for variable in variables:
            grouped_values = defaultdict(set)
            for row in truth_table:
                key = tuple(
                    row.assignment[current_name]
                    for current_name in variables
                    if current_name != variable
                )
                grouped_values[key].add(row.value)
            if all(len(values) == 1 for values in grouped_values.values()):
                fictive_variables.append(variable)
        return tuple(fictive_variables)
