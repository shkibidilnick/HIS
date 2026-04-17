import unittest

from lab2_sem4.core.expression import BooleanExpressionFactory
from lab2_sem4.core.tokenizer import Tokenizer, TokenizerError


class TokenizerParserTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tokenizer = Tokenizer()
        self.factory = BooleanExpressionFactory()

    def test_tokenizer_supports_ascii_and_unicode(self) -> None:
        tokens = self.tokenizer.tokenize('!(a&b)→c')
        token_values = [token.value for token in tokens[:-1]]
        self.assertEqual(['!', '(', 'a', '&', 'b', ')', '→', 'c'], token_values)

    def test_tokenizer_rejects_invalid_symbol(self) -> None:
        with self.assertRaises(TokenizerError):
            self.tokenizer.tokenize('a+b')

    def test_parser_honors_operator_priority(self) -> None:
        expression = self.factory.create('a|b&c')
        self.assertEqual(1, expression.evaluate({'a': 1, 'b': 0, 'c': 0}))
        self.assertEqual(0, expression.evaluate({'a': 0, 'b': 1, 'c': 0}))

    def test_implication_and_equivalence_work(self) -> None:
        implication = self.factory.create('a->b')
        equivalence = self.factory.create('a~b')
        self.assertEqual(0, implication.evaluate({'a': 1, 'b': 0}))
        self.assertEqual(1, equivalence.evaluate({'a': 1, 'b': 1}))
        self.assertEqual(0, equivalence.evaluate({'a': 1, 'b': 0}))

    def test_factory_limits_variable_count(self) -> None:
        with self.assertRaises(ValueError):
            self.factory.create('a&b&c&d&e&f')


if __name__ == '__main__':
    unittest.main()
