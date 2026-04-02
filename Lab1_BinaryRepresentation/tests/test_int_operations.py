import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from constants import POSITIVE_SIGN, NEGATIVE_SIGN, MAX_VALUE, MIN_VALUE, BIT_SIZE
from integer.converter import to_complementary_code
from integer.operations import add_complementary_numbers, subtract_complementary_bits, multiply_direct_numbers, divide_direct_numbers

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

class TestIntegerDivision(unittest.TestCase):

    def test_div_positive_exact(self):
        """Test 10 / 2 = 5.0 (witch is exact result)"""
        int_bits, frac_bits, sign, val = divide_direct_numbers(10, 2)
        self.assertEqual(val, 5.0)
        expected_int_bits = [POSITIVE_SIGN] + [0] * (BIT_SIZE - 1 - 3) + [1, 0, 1]
        self.assertEqual(int_bits, expected_int_bits)
        self.assertEqual(sign, POSITIVE_SIGN)
        self.assertEqual(frac_bits, [0])

    def test_div_positive_recurring(self):
        """Test 10 / 3 = 3.(3) (Recurring fraction)"""
        int_bits, frac_bits, sign, val = divide_direct_numbers(10, 3)
        self.assertAlmostEqual(val, 10/3, places=5)
        expected_int_bits = [POSITIVE_SIGN] + [0] * (BIT_SIZE - 1 - 2) + [1, 1]
        self.assertEqual(int_bits, expected_int_bits)
        self.assertEqual(sign, POSITIVE_SIGN)
        expected_frac_start = [0, 1, 0, 1, 0, 1]
        self.assertEqual(frac_bits[:6], expected_frac_start)

    def test_div_negative_exact(self):
        int_bits, frac_bits, sign, val = divide_direct_numbers(-10, 2)
        self.assertEqual(val, -5.0)
        expected_int_bits = [NEGATIVE_SIGN] + [0] * (BIT_SIZE - 1 - 3) + [1, 0, 1]
        self.assertEqual(int_bits, expected_int_bits)
        self.assertEqual(sign, NEGATIVE_SIGN)
        self.assertEqual(frac_bits, [0])

    def test_div_zero_by_number(self):
        int_bits, frac_bits, sign, val = divide_direct_numbers(0, 5)
        self.assertEqual(val, 0.0)
        self.assertEqual(int_bits, [0] * BIT_SIZE)
        self.assertEqual(frac_bits, [0])

    def test_div_small_by_large(self):
        """Test 2 / 10 = 0.2"""
        int_bits, frac_bits, sign, val = divide_direct_numbers(2, 10)
        self.assertAlmostEqual(val, 0.2, places=5)
        self.assertEqual(int_bits, [0] * BIT_SIZE)
        expected_frac_start = [0, 0, 1, 1, 0, 0, 1, 1]
        self.assertEqual(frac_bits[:8], expected_frac_start)

    def test_div_by_zero(self):
        """Test 10 / 0 -> ZeroDivisionError"""
        with self.assertRaises(ZeroDivisionError):
            divide_direct_numbers(10, 0)

    def test_div_max_value_boundary(self):
        """Test MAX / 1 = MAX (Boundary case for 31 bits)"""
        int_bits, frac_bits, sign, val = divide_direct_numbers(MAX_VALUE, 1)

        self.assertEqual(val, MAX_VALUE)
        self.assertEqual(sign, POSITIVE_SIGN)

        expected_mag = [1] * (BIT_SIZE - 1)
        self.assertEqual(int_bits[1:], expected_mag)
        self.assertEqual(frac_bits, [0])

if __name__ == '__main__':
    unittest.main()


