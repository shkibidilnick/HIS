import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from integer.converter import to_direct_code, to_reverse_code, to_complementary_code
from constants import BIT_SIZE, POSITIVE_SIGN, NEGATIVE_SIGN, MAX_VALUE


class TestDirectCode(unittest.TestCase):
    def test_zero(self):
        result = to_direct_code(0)
        expected = [0] * BIT_SIZE
        self.assertEqual(result, expected, "Number 0 must be with 32 zeros.")

    def test_positive_small_number(self):
        result = to_direct_code(10)
        self.assertEqual(result[0], POSITIVE_SIGN, "Sign must be positive.")
        self.assertEqual(result[-4:], [1, 0, 1, 0], "The bits of the number 10 must be 1010.")

    def test_negative_small_number(self):
        result = to_direct_code(-10)
        self.assertEqual(result[0], NEGATIVE_SIGN, "Sign must be negative.")
        self.assertEqual(result[-4:], [1, 0, 1, 0], "The bits of modulus of the number 10 must be 1010.")

    def test_large_number_no_padding(self):
        large_val = 2**30
        result = to_direct_code(large_val)
        expected = [POSITIVE_SIGN] + [1] + [0] * 30
        self.assertEqual(result, expected, "A large number must fill the entire digit without addition.")

    def test_overflow_error(self):
        too_large = MAX_VALUE + 1
        with self.assertRaises(ValueError) as context:
            to_direct_code(too_large)

        self.assertIn("too large", str(context.exception))

class TestReverseCode(unittest.TestCase):

    def test_positive_number(self):
        """Test positive number: should be same as direct code"""
        result = to_reverse_code(10)
        self.assertEqual(result[0], POSITIVE_SIGN)
        self.assertEqual(result[-4:], [1, 0, 1, 0])

    def test_zero(self):
        """Test zero: should be all zeros (not ones)"""
        result = to_reverse_code(0)
        expected = [0] * BIT_SIZE
        self.assertEqual(result, expected)

    def test_negative_number(self):
        """Test negative number: absolute bits should be inverted"""
        result = to_reverse_code(-10)
        self.assertEqual(result[0], NEGATIVE_SIGN)
        self.assertEqual(result[-4:], [0, 1, 0, 1], "Abso;ute bits should be inverted")

    def test_negative_one(self):
        """Special  case: sign 1 + all ones except final 0 """
        result = to_reverse_code(-1)
        expected = [NEGATIVE_SIGN] + [1] * (BIT_SIZE - 2) + [0]
        self.assertEqual(result, expected, "-1 in reverse should be sign bit + all ones except final 0")

class TestComplementaryCode(unittest.TestCase):

    def test_positive_number(self):
        result = to_complementary_code(10)
        self.assertEqual(result[0], POSITIVE_SIGN)
        self.assertEqual(result[-4:], [1, 0, 1, 0])

    def test_zero(self):
        result = to_complementary_code(0)
        expected = [0] * BIT_SIZE
        self.assertEqual(result, expected)

    def test_negative_number(self):
        result = to_complementary_code(-10)
        self.assertEqual(result[0], NEGATIVE_SIGN)
        self.assertEqual(result[-4:], [0, 1, 1, 0], "Should be reverse code + 1")

    def test_negative_one(self):
        """All bits should be 1"""
        result = to_complementary_code(-1)
        expected = [NEGATIVE_SIGN] + [1] * (BIT_SIZE - 1)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()