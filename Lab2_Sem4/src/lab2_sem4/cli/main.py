"""Console entry point."""
from __future__ import annotations

from lab2_sem4.formatting.report_formatter import ReportFormatter
from lab2_sem4.service import BooleanFunctionService


def main() -> None:
    print('Lab2_Sem4 - Boolean Function Analyzer')
    expression = input('Enter boolean expression: ').strip()
    service = BooleanFunctionService()
    formatter = ReportFormatter()
    report = service.analyze(expression)
    print()
    print(formatter.format(report))


if __name__ == '__main__':
    main()
