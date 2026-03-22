import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from utils import add_binary_lists

class TestBinaryAddition(unittest.TestCase):

    def test_simple_addition_no_carry(self):
        """1 + 1 = 2: 01 + 01 = 10"""
        a = [0, 1]
        b = [0, 1]
        result = add_binary_lists(a, b)
        expected = [1, 0]
        self.assertEqual(result, expected)

    def test_addition_with_carry_out(self):
        """3 + 1 = 4: 11 + 01 = 100"""
        a = [1, 1]
        # test padding additionally
        b = [1]
        result = add_binary_lists(a, b)
        expected = [1, 0, 0]
        self.assertEqual(result, expected, "Should handle carry out correctly")

    def test_full_carry(self):
        """3 + 3 = 6: 11 + 11 = 110"""
        # test padding additionally
        a = [1, 1]
        b = [1, 1]
        result = add_binary_lists(a, b)
        expected = [1, 1, 0]
        self.assertEqual(result, expected)

    def test_padding_and_result(self):
        a = [0, 0, 1, 1]
        b = [0, 1, 1]
        result = add_binary_lists(a, b)
        expected = [0, 1, 1, 0]
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()


