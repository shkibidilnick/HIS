"""Console report formatter."""
from __future__ import annotations

from typing import Iterable, Sequence

from lab2_sem4.models import (
    AnalysisReport,
    CoverageTable,
    DerivativeResult,
    KarnaughMapResult,
    MinimizationResult,
    TruthTableRow,
)


class ReportFormatter:
    def format(self, report: AnalysisReport) -> str:
        sections = [
            self._format_heading('Expression'),
            report.expression,
            self._format_heading('Truth table'),
            self._format_truth_table(report.truth_table, report.variables),
            self._format_heading('Normal forms'),
            self._format_normal_forms(report),
            self._format_heading('Post classes'),
            self._format_post_classes(report),
            self._format_heading('Zhegalkin polynomial'),
            report.zhegalkin_polynomial,
            self._format_heading('Fictive variables'),
            ', '.join(report.fictive_variables) if report.fictive_variables else 'None',
            self._format_heading('First-order derivatives'),
            self._format_derivatives(report.first_order_derivatives),
            self._format_heading('Second-order derivatives'),
            self._format_derivatives(report.second_order_derivatives),
            self._format_heading('Third-order derivatives'),
            self._format_derivatives(report.third_order_derivatives),
            self._format_heading('Fourth-order derivatives'),
            self._format_derivatives(report.fourth_order_derivatives),
            self._format_heading('DNF minimization'),
            self._format_minimization(report.dnf_minimization),
            self._format_heading('CNF minimization'),
            self._format_minimization(report.cnf_minimization),
            self._format_heading('Karnaugh map'),
            self._format_karnaugh_map(report.karnaugh_map),
        ]
        return '\n\n'.join(sections)

    @staticmethod
    def _format_heading(title: str) -> str:
        return title + '\n' + '-' * len(title)

    @staticmethod
    def _format_truth_table(truth_table: Sequence[TruthTableRow], variables: Sequence[str]) -> str:
        headers = ['#', *variables, 'f']
        rows = []
        for row in truth_table:
            values = [str(row.index)] + [str(row.assignment[variable]) for variable in variables] + [str(row.value)]
            rows.append(values)
        return _render_table(headers, rows)

    @staticmethod
    def _format_normal_forms(report: AnalysisReport) -> str:
        normal_forms = report.normal_forms
        lines = [
            f'SDNF: {normal_forms.sdnf}',
            f'SKNF: {normal_forms.sknf}',
            f'SDNF numeric: {normal_forms.sdnf_numeric}',
            f'SKNF numeric: {normal_forms.sknf_numeric}',
            f'Index form: {normal_forms.index_form}',
        ]
        return '\n'.join(lines)

    @staticmethod
    def _format_post_classes(report: AnalysisReport) -> str:
        classes = report.post_classes
        return '\n'.join(
            [
                f'T0: {classes.preserves_zero}',
                f'T1: {classes.preserves_one}',
                f'S: {classes.self_dual}',
                f'M: {classes.monotonic}',
                f'L: {classes.linear}',
            ]
        )

    def _format_derivatives(self, derivatives: Sequence[DerivativeResult]) -> str:
        if not derivatives:
            return 'None'
        lines = []
        for derivative in derivatives:
            variable_part = ''.join(derivative.variables)
            lines.append(f'∂/{variable_part}: {derivative.expression}')
        return '\n'.join(lines)

    def _format_minimization(self, result: MinimizationResult) -> str:
        lines = [f'Result: {result.expression}']
        for stage_index, stage in enumerate(result.stages, start=1):
            lines.append(f'Stage {stage_index}:')
            lines.append(f'  input: {stage.input_terms}')
            lines.append(f'  combined: {stage.combined_terms}')
            if stage.combinations:
                for combination in stage.combinations:
                    lines.append(f'  {combination}')
        lines.append('Coverage table:')
        lines.append(self._format_coverage_table(result.coverage_table))
        return '\n'.join(lines)

    @staticmethod
    def _format_coverage_table(table: CoverageTable) -> str:
        headers = ['term', *table.headers]
        rows = []
        for row_name, row_cells in zip(table.row_names, table.cells):
            rows.append([row_name, *('X' if cell else '' for cell in row_cells)])
        return _render_table(headers, rows)

    @staticmethod
    def _format_karnaugh_map(result: KarnaughMapResult | None) -> str:
        if result is None:
            return 'Karnaugh map is unavailable only when variable count exceeds supported limit.'

        row_variable_count = len(result.variable_order) // 2
        row_variable_names = ''.join(result.variable_order[:row_variable_count]) or '∅'
        column_variable_names = ''.join(result.variable_order[row_variable_count:]) or '∅'

        headers = [f'{row_variable_names}\\{column_variable_names}', *result.column_labels]
        rows = [[label, *map(str, values)] for label, values in zip(result.row_labels, result.grid)]

        lines = [
            _render_table(headers, rows),
            f'DNF from map: {result.dnf_expression}',
            f'CNF from map: {result.cnf_expression}',
        ]
        return '\n'.join(lines)

def _render_table(headers: Sequence[str], rows: Iterable[Sequence[str]]) -> str:
    rows = list(rows)
    widths = [len(header) for header in headers]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))
    rendered_rows = []
    rendered_rows.append(' | '.join(header.ljust(widths[index]) for index, header in enumerate(headers)))
    rendered_rows.append('-+-'.join('-' * width for width in widths))
    for row in rows:
        rendered_rows.append(' | '.join(cell.ljust(widths[index]) for index, cell in enumerate(row)))
    return '\n'.join(rendered_rows)
