import io
import unittest
from unittest.mock import patch

from lab2_sem4.cli.main import main
from lab2_sem4.formatting.report_formatter import ReportFormatter
from lab2_sem4.service import BooleanFunctionService


class CliAndFormatterTests(unittest.TestCase):
    def test_formatter_contains_main_sections(self) -> None:
        report = BooleanFunctionService().analyze('(a&b)|c')
        formatted = ReportFormatter().format(report)
        self.assertIn('Truth table', formatted)
        self.assertIn('Zhegalkin polynomial', formatted)
        self.assertIn('DNF minimization', formatted)

    def test_cli_prints_report(self) -> None:
        stdout = io.StringIO()
        with patch('builtins.input', return_value='(a&b)|c'), patch('sys.stdout', stdout):
            main()
        output = stdout.getvalue()
        self.assertIn('Lab2_Sem4 - Boolean Function Analyzer', output)
        self.assertIn('Index form: 01010111', output)


if __name__ == '__main__':
    unittest.main()
