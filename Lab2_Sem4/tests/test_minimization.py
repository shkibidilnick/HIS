import unittest

from lab2_sem4.minimization.common import mask_to_cnf_clause, mask_to_dnf_term
from lab2_sem4.minimization.quine_mccluskey import ExactMinimizer
from lab2_sem4.service import BooleanFunctionService


class MinimizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dnf_minimizer = ExactMinimizer(mask_to_dnf_term, ' ∨ ')
        self.cnf_minimizer = ExactMinimizer(mask_to_cnf_clause, ' ∧ ')
        self.service = BooleanFunctionService()

    def test_exact_dnf_minimization(self) -> None:
        result = self.dnf_minimizer.minimize([1, 3, 5, 6, 7], ('a', 'b', 'c'))
        self.assertEqual('(c) ∨ (a ∧ b)', result.expression)
        self.assertTrue(result.coverage_table.headers)
        self.assertTrue(result.stages)

    def test_exact_cnf_minimization(self) -> None:
        result = self.cnf_minimizer.minimize([0, 2, 4], ('a', 'b', 'c'))
        self.assertIn(result.expression, {'(a ∨ c) ∧ (b ∨ c)', '(b ∨ c) ∧ (a ∨ c)'})

    def test_karnaugh_map_is_built_for_three_variables(self) -> None:
        report = self.service.analyze('(a&b)|c')
        self.assertIsNotNone(report.karnaugh_map)
        self.assertEqual('(c) ∨ (a ∧ b)', report.karnaugh_map.dnf_expression)
        self.assertEqual('(a ∨ c) ∧ (b ∨ c)', report.karnaugh_map.cnf_expression)

    def test_karnaugh_map_is_built_for_five_variables(self) -> None:
        report = self.service.analyze('a|b|c|d|e')
        self.assertIsNotNone(report.karnaugh_map)
        self.assertEqual(('00', '01', '11', '10'), report.karnaugh_map.row_labels)
        self.assertEqual(
            ('000', '001', '011', '010', '110', '111', '101', '100'),
            report.karnaugh_map.column_labels,
        )

    def test_karnaugh_map_grid_shape_for_five_variables(self) -> None:
        report = self.service.analyze('a|b|c|d|e')
        self.assertIsNotNone(report.karnaugh_map)
        self.assertEqual(4, len(report.karnaugh_map.grid))
        self.assertTrue(all(len(row) == 8 for row in report.karnaugh_map.grid))


if __name__ == '__main__':
    unittest.main()
