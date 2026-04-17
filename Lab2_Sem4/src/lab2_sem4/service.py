"""Facade over all analysis steps."""
from __future__ import annotations

from lab2_sem4.analysis.derivatives import BooleanDerivativeAnalyzer
from lab2_sem4.analysis.fictive_variables import FictiveVariableAnalyzer
from lab2_sem4.analysis.normal_forms import NormalFormBuilder
from lab2_sem4.analysis.post_classes import PostClassAnalyzer
from lab2_sem4.analysis.truth_table import TruthTableBuilder
from lab2_sem4.analysis.zhegalkin import ZhegalkinBuilder
from lab2_sem4.core.expression import BooleanExpressionFactory
from lab2_sem4.minimization.common import mask_to_cnf_clause, mask_to_dnf_term
from lab2_sem4.minimization.karnaugh import KarnaughMapBuilder
from lab2_sem4.minimization.quine_mccluskey import ExactMinimizer
from lab2_sem4.models import AnalysisReport


class BooleanFunctionService:
    def __init__(self) -> None:
        self._expression_factory = BooleanExpressionFactory()
        self._truth_table_builder = TruthTableBuilder()
        self._normal_form_builder = NormalFormBuilder()
        self._post_class_analyzer = PostClassAnalyzer()
        self._zhegalkin_builder = ZhegalkinBuilder()
        self._fictive_variable_analyzer = FictiveVariableAnalyzer()
        self._derivative_analyzer = BooleanDerivativeAnalyzer()
        self._dnf_minimizer = ExactMinimizer(mask_to_dnf_term, ' ∨ ')
        self._cnf_minimizer = ExactMinimizer(mask_to_cnf_clause, ' ∧ ')
        self._karnaugh_builder = KarnaughMapBuilder()

    def analyze(self, source: str) -> AnalysisReport:
        expression = self._expression_factory.create(source)
        truth_table = self._truth_table_builder.build(expression)
        normal_forms = self._normal_form_builder.build(expression.variables, truth_table)
        post_classes = self._post_class_analyzer.analyze(truth_table)
        polynomial, is_linear = self._zhegalkin_builder.build(expression.variables, truth_table)
        post_classes = post_classes.__class__(
            preserves_zero=post_classes.preserves_zero,
            preserves_one=post_classes.preserves_one,
            self_dual=post_classes.self_dual,
            monotonic=post_classes.monotonic,
            linear=is_linear,
        )
        fictive_variables = self._fictive_variable_analyzer.find(expression.variables, truth_table)
        first_order = self._derivative_analyzer.build_for_order(expression.variables, truth_table, 1)
        second_order = self._derivative_analyzer.build_for_order(expression.variables, truth_table, 2)
        third_order = self._derivative_analyzer.build_for_order(expression.variables, truth_table, 3)
        fourth_order = self._derivative_analyzer.build_for_order(expression.variables, truth_table, 4)
        one_indices = [row.index for row in truth_table if row.value == 1]
        zero_indices = [row.index for row in truth_table if row.value == 0]
        dnf_minimization = self._dnf_minimizer.minimize(one_indices, expression.variables)
        cnf_minimization = self._cnf_minimizer.minimize(zero_indices, expression.variables)
        karnaugh_map = self._karnaugh_builder.build(expression.variables, truth_table)
        return AnalysisReport(
            expression=source,
            variables=expression.variables,
            truth_table=truth_table,
            normal_forms=normal_forms,
            post_classes=post_classes,
            zhegalkin_polynomial=polynomial,
            fictive_variables=fictive_variables,
            first_order_derivatives=first_order,
            second_order_derivatives=second_order,
            third_order_derivatives=third_order,
            fourth_order_derivatives=fourth_order,
            dnf_minimization=dnf_minimization,
            cnf_minimization=cnf_minimization,
            karnaugh_map=karnaugh_map,
        )
