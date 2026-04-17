import unittest

from lab2_sem4.analysis.normal_forms import NormalFormBuilder
from lab2_sem4.analysis.truth_table import TruthTableBuilder
from lab2_sem4.core.expression import BooleanExpressionFactory


class TruthTableAndFormsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.factory = BooleanExpressionFactory()
        self.truth_builder = TruthTableBuilder()
        self.form_builder = NormalFormBuilder()

    def test_truth_table_for_a_and_b_or_c(self) -> None:
        expression = self.factory.create('(a&b)|c')
        truth_table = self.truth_builder.build(expression)
        values = [row.value for row in truth_table]
        self.assertEqual([0, 1, 0, 1, 0, 1, 1, 1], values)

    def test_normal_forms_and_numeric_forms(self) -> None:
        expression = self.factory.create('(a&b)|c')
        truth_table = self.truth_builder.build(expression)
        normal_forms = self.form_builder.build(expression.variables, truth_table)
        self.assertEqual('Σ(1, 3, 5, 6, 7)', normal_forms.sdnf_numeric)
        self.assertEqual('Π(0, 2, 4)', normal_forms.sknf_numeric)
        self.assertEqual('01010111', normal_forms.index_form)
        self.assertIn('(a ∧ b ∧ ¬c)', normal_forms.sdnf)
        self.assertIn('(¬a ∨ b ∨ c)', normal_forms.sknf)


if __name__ == '__main__':
    unittest.main()
