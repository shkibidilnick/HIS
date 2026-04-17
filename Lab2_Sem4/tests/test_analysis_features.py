import unittest

from lab2_sem4.service import BooleanFunctionService


class AnalysisFeatureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = BooleanFunctionService()
        self.report = self.service.analyze('(a&b)|c')

    def test_post_classes(self) -> None:
        self.assertTrue(self.report.post_classes.preserves_zero)
        self.assertTrue(self.report.post_classes.preserves_one)
        self.assertFalse(self.report.post_classes.self_dual)
        self.assertTrue(self.report.post_classes.monotonic)
        self.assertFalse(self.report.post_classes.linear)

    def test_zhegalkin_polynomial(self) -> None:
        self.assertEqual('c ⊕ ab ⊕ abc', self.report.zhegalkin_polynomial)

    def test_fictive_variables(self) -> None:
        self.assertEqual(tuple(), self.report.fictive_variables)
        report = self.service.analyze('a')
        self.assertEqual(tuple(), report.fictive_variables)

    def test_derivatives_of_first_second_and_third_order(self) -> None:
        first_order = {''.join(item.variables): item.expression for item in self.report.first_order_derivatives}
        second_order = {''.join(item.variables): item.expression for item in self.report.second_order_derivatives}
        third_order = {''.join(item.variables): item.expression for item in self.report.third_order_derivatives}
        self.assertEqual('(b ∧ ¬c)', first_order['a'])
        self.assertEqual('(a ∧ ¬c)', first_order['b'])
        self.assertEqual('(¬a ∧ ¬b) ∨ (¬a ∧ b) ∨ (a ∧ ¬b)', first_order['c'])
        self.assertEqual('(¬c)', second_order['ab'])
        self.assertEqual('(b)', second_order['ac'])
        self.assertEqual('(a)', second_order['bc'])
        self.assertEqual('1', third_order['abc'])


if __name__ == '__main__':
    unittest.main()
