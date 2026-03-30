import unittest
import sys
import os

from constants import POSITIVE_SIGN, NEGATIVE_SIGN, MAX_VALUE, MIN_VALUE, BIT_SIZE
from integer.converter import to_complementary_code, from_complementary_code

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from integer.operations import add_complementary_numbers, subtract_complementary_bits, multiply_direct_numbers


class TestIntegerAddition(unittest.TestCase):

    def test_add_positive_numbers(self):
        bits, val, overflow = add_complementary_numbers(10, 5)
        expected_bits = [POSITIVE_SIGN] + [0] * (len(bits) - 1 - 4) + [1, 1, 1, 1]
        self.assertEqual(val, 15)
        self.assertEqual(bits, expected_bits)
        self.assertFalse(overflow, "Should not overflow")

    def test_add_negative_numbers(self):
        bits, val, overflow = add_complementary_numbers(-10, -5)
        expected_bits = [NEGATIVE_SIGN] + [1] * (len(bits) - 1 - 4) + [0, 0, 0, 1]
        self.assertEqual(val, -15)
        self.assertEqual(bits, expected_bits)
        self.assertFalse(overflow, "Should not overflow")

    def test_add_mixed_numbers(self):
        bits, val, overflow = add_complementary_numbers(10, -5)
        expected_bits = [POSITIVE_SIGN] + [0] * (len(bits) - 1 - 3) + [1, 0, 1]
        self.assertEqual(val, 5)
        self.assertEqual(bits, expected_bits)
        self.assertFalse(overflow, "Should not overflow")

    def test_positive_overflow_detection(self):
        """
        MAX + 1. Result wraps to MIN, Overflow Flag should be True.
        """
        bits, val, overflow = add_complementary_numbers(MAX_VALUE, 1)

        expected_wrapped_value = MIN_VALUE

        self.assertEqual(val, expected_wrapped_value, "Value should wrap to MIN")
        self.assertTrue(overflow, "Overflow flag should be raised for MAX + 1")

    def test_negative_overflow_detection(self):
        """
        MIN + (-1). Result wraps to MAX, Overflow Flag should be True.
        """
        bits, val, overflow = add_complementary_numbers(MIN_VALUE, -1)

        expected_wrapped_value = MAX_VALUE

        self.assertEqual(val, expected_wrapped_value, "Value should wrap to MAX")
        self.assertTrue(overflow, "Overflow flag should be raised for MIN - 1")

class TestIntegerSubtraction(unittest.TestCase):

    def test_sub_positive_numbers(self):
        a = to_complementary_code(10)
        b = to_complementary_code(5)

        bits, val, overflow = subtract_complementary_bits(a, b)
        expected_bits = [POSITIVE_SIGN] + [0] * (len(bits) - 1 - 3) + [1, 0, 1]
        self.assertEqual(bits, expected_bits)
        self.assertEqual(val, 5)
        self.assertFalse(overflow)

    def test_sub_negative_from_positive(self):
        a = to_complementary_code(10)
        b = to_complementary_code(-5)

        bits, val, overflow = subtract_complementary_bits(a, b)
        expected_bits = [POSITIVE_SIGN] + [0] * (len(bits) - 1 - 4) + [1, 1, 1, 1]
        self.assertEqual(bits, expected_bits)
        self.assertEqual(val, 15)
        self.assertFalse(overflow)

    def test_positive_overflow_subtraction(self):
        """
        MAX - (-1) -> Overflow
        """
        a = to_complementary_code(MAX_VALUE)
        b = to_complementary_code(-1)

        bits, val, overflow = subtract_complementary_bits(a, b)

        self.assertTrue(overflow)
        # Result wraps to MIN_VALUE
        self.assertEqual(val, MIN_VALUE)

    def test_negative_overflow_subtraction(self):
        """
        MIN -1 -> Overflow
        """
        a = to_complementary_code(MIN_VALUE)
        b = to_complementary_code(1)

        bits, val, overflow = subtract_complementary_bits(a, b)

        self.assertTrue(overflow)
        # Result must be equal to MIN_VALUE
        self.assertEqual(val, MAX_VALUE)

class TestIntegerMultiplication(unittest.TestCase):

    def test_mul_positive_numbers(self):
        bits, val, overflow = multiply_direct_numbers(10, 5)
        expected_bits = [POSITIVE_SIGN] + [0] * (len(bits) - 1 - 6) + [1, 1, 0, 0, 1, 0]
        self.assertEqual(bits, expected_bits)
        self.assertEqual(val, 50)
        self.assertFalse(overflow)

    def test_mul_negative_numbers(self):
        bits, val, overflow = multiply_direct_numbers(-10, -5)
        expected_bits = [POSITIVE_SIGN] + [0] * (len(bits) - 1 - 6) + [1, 1, 0, 0, 1, 0]
        self.assertEqual(bits, expected_bits)
        self.assertEqual(val, 50)
        self.assertFalse(overflow)

    def test_mul_mixed_numbers(self):
        bits, val, overflow = multiply_direct_numbers(-10, 5)
        expected_bits = [NEGATIVE_SIGN] + [0] * (len(bits) - 1 - 6) + [1, 1, 0, 0, 1, 0]
        self.assertEqual(bits, expected_bits)
        self.assertEqual(val, -50)
        self.assertFalse(overflow)

    def test_mul_by_zero(self):
        bits, val, overflow = multiply_direct_numbers(-15, 0)
        expected_bits = [0] * BIT_SIZE
        self.assertEqual(bits, expected_bits)
        self.assertEqual(val, 0)
        self.assertFalse(overflow)

    def test_mul_overflow_detection(self):
        val_a = 2**30
        val_b = 2
        bits, val, overflow = multiply_direct_numbers(val_a, val_b)

        self.assertTrue(overflow, "Overflow should be detected")

if __name__ == '__main__':
    unittest.main()


