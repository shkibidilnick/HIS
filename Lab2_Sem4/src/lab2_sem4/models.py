"""Data models used by the application."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

Bit = int
BitTuple = Tuple[Bit, ...]
MaskBit = Optional[Bit]
Mask = Tuple[MaskBit, ...]


@dataclass(frozen=True)
class Token:
    token_type: str
    value: str


@dataclass(frozen=True)
class TruthTableRow:
    index: int
    assignment: Dict[str, Bit]
    value: Bit


@dataclass(frozen=True)
class NormalForms:
    sdnf: str
    sknf: str
    sdnf_numeric: str
    sknf_numeric: str
    index_form: str


@dataclass(frozen=True)
class PostClasses:
    preserves_zero: bool
    preserves_one: bool
    self_dual: bool
    monotonic: bool
    linear: bool


@dataclass(frozen=True)
class DerivativeResult:
    variables: Tuple[str, ...]
    values: Dict[BitTuple, Bit]
    expression: str


@dataclass(frozen=True)
class MinimizationStage:
    input_terms: Tuple[Mask, ...]
    combined_terms: Tuple[Mask, ...]
    combinations: Tuple[str, ...]


@dataclass(frozen=True)
class CoverageTable:
    headers: Tuple[str, ...]
    row_names: Tuple[str, ...]
    cells: Tuple[Tuple[bool, ...], ...]


@dataclass(frozen=True)
class MinimizationResult:
    prime_implicants: Tuple[Mask, ...]
    selected_implicants: Tuple[Mask, ...]
    stages: Tuple[MinimizationStage, ...]
    coverage_table: CoverageTable
    expression: str


@dataclass(frozen=True)
class KarnaughMapResult:
    variable_order: Tuple[str, ...]
    row_labels: Tuple[str, ...]
    column_labels: Tuple[str, ...]
    grid: Tuple[Tuple[Bit, ...], ...]
    dnf_expression: str
    cnf_expression: str


@dataclass(frozen=True)
class AnalysisReport:
    expression: str
    variables: Tuple[str, ...]
    truth_table: Tuple[TruthTableRow, ...]
    normal_forms: NormalForms
    post_classes: PostClasses
    zhegalkin_polynomial: str
    fictive_variables: Tuple[str, ...]
    first_order_derivatives: Tuple[DerivativeResult, ...]
    second_order_derivatives: Tuple[DerivativeResult, ...]
    third_order_derivatives: Tuple[DerivativeResult, ...]
    fourth_order_derivatives: Tuple[DerivativeResult, ...]
    dnf_minimization: MinimizationResult
    cnf_minimization: MinimizationResult
    karnaugh_map: Optional[KarnaughMapResult]
