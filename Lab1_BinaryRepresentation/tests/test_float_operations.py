import math
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from constants import (
    POSITIVE_SIGN,
    NEGATIVE_SIGN,
    FLOAT_EXP_BITS,
    FLOAT_MANTISSA_BITS,
    FLOAT_BIT_SIZE,
)
from floating_point.converter import from_ieee754
from floating_point.operations import (
    _build_nan_bits,
    _build_zero_bits,
    _build_infinity_bits,
    _pad_left,
    _is_zero,
    _is_infinity,
    _is_nan,
    _parse_float,
    _assemble_result,
    add_floats,
    sub_floats,
    mul_floats,
    div_floats,
)


class TestFloatOperationHelpers(unittest.TestCase):

    def test_build_nan_bits(self):
        bits = _build_nan_bits()
        self.assertEqual(bits[0], POSITIVE_SIGN)
        self.assertEqual(bits[1:1 + FLOAT_EXP_BITS], [1] * FLOAT_EXP_BITS)
        self.assertTrue(any(bit == 1 for bit in bits[1 + FLOAT_EXP_BITS:]))

    def test_build_zero_bits(self):
        expected = [NEGATIVE_SIGN] + [0] * (FLOAT_BIT_SIZE - 1)
        self.assertEqual(_build_zero_bits(NEGATIVE_SIGN), expected)

    def test_build_infinity_bits(self):
        bits = _build_infinity_bits(POSITIVE_SIGN)
        self.assertEqual(bits[0], POSITIVE_SIGN)
        self.assertEqual(bits[1:1 + FLOAT_EXP_BITS], [1] * FLOAT_EXP_BITS)
        self.assertEqual(bits[1 + FLOAT_EXP_BITS:], [0] * FLOAT_MANTISSA_BITS)

    def test_pad_left(self):
        self.assertEqual(_pad_left([1, 1], 4), [0, 0, 1, 1])

    def test_is_zero(self):
        self.assertTrue(_is_zero(0, 0))
        self.assertFalse(_is_zero(1, 0))

    def test_is_infinity(self):
        self.assertTrue(_is_infinity((1 << FLOAT_EXP_BITS) - 1, 0))
        self.assertFalse(_is_infinity(1, 0))

    def test_is_nan(self):
        self.assertTrue(_is_nan((1 << FLOAT_EXP_BITS) - 1, 1))
        self.assertFalse(_is_nan((1 << FLOAT_EXP_BITS) - 1, 0))

    def test_parse_float(self):
        bits, sign, exponent, mantissa, significand = _parse_float(1.0)

        self.assertEqual(bits[0], POSITIVE_SIGN)
        self.assertEqual(sign, POSITIVE_SIGN)
        self.assertEqual(exponent, 127)
        self.assertEqual(mantissa, 0)
        self.assertEqual(significand, 1 << FLOAT_MANTISSA_BITS)

    def test_assemble_result_zero(self):
        bits, value = _assemble_result(POSITIVE_SIGN, 0, 0)
        self.assertEqual(bits, [0] * FLOAT_BIT_SIZE)
        self.assertEqual(value, 0.0)

    def test_assemble_result_overflow(self):
        bits, value = _assemble_result(POSITIVE_SIGN, 255, 1 << FLOAT_MANTISSA_BITS)
        self.assertEqual(bits[1:1 + FLOAT_EXP_BITS], [1] * FLOAT_EXP_BITS)
        self.assertEqual(value, float("inf"))

    def test_assemble_result_underflow(self):
        bits, value = _assemble_result(POSITIVE_SIGN, 0, 1 << FLOAT_MANTISSA_BITS)
        self.assertEqual(bits, [0] * FLOAT_BIT_SIZE)
        self.assertEqual(value, 0.0)

    def test_assemble_result_normalization_right(self):
        bits, value = _assemble_result(POSITIVE_SIGN, 127, 1 << 24)
        self.assertAlmostEqual(value, 2.0, places=5)

    def test_assemble_result_normalization_left(self):
        bits, value = _assemble_result(POSITIVE_SIGN, 128, 1 << 22)
        self.assertAlmostEqual(value, 1.0, places=5)


class TestFloatAddition(unittest.TestCase):

    def test_add_positive_numbers(self):
        bits, value = add_floats(1.5, 2.25)
        self.assertEqual(bits[0], POSITIVE_SIGN)
        self.assertAlmostEqual(value, 3.75, places=5)

    def test_add_negative_numbers(self):
        bits, value = add_floats(-1.5, -2.25)
        self.assertEqual(bits[0], NEGATIVE_SIGN)
        self.assertAlmostEqual(value, -3.75, places=5)

    def test_add_mixed_sign_numbers(self):
        bits, value = add_floats(2.5, -1.25)
        self.assertEqual(bits[0], POSITIVE_SIGN)
        self.assertAlmostEqual(value, 1.25, places=5)

    def test_add_opposite_numbers(self):
        bits, value = add_floats(1.0, -1.0)
        self.assertEqual(bits, [0] * FLOAT_BIT_SIZE)
        self.assertEqual(value, 0.0)

    def test_add_infinity_and_number(self):
        bits, value = add_floats(float("inf"), 2.0)
        self.assertEqual(bits[0], POSITIVE_SIGN)
        self.assertEqual(value, float("inf"))

    def test_add_opposite_infinities(self):
        bits, value = add_floats(float("inf"), float("-inf"))
        self.assertTrue(math.isnan(value))
        self.assertTrue(math.isnan(from_ieee754(bits)))

    def test_add_nan(self):
        bits, value = add_floats(float("nan"), 1.0)
        self.assertTrue(math.isnan(value))
        self.assertTrue(math.isnan(from_ieee754(bits)))

    def test_add_zero_zero(self):
        bits, value = add_floats(0.0, 0.0)
        self.assertEqual(bits, [0] * FLOAT_BIT_SIZE)
        self.assertEqual(value, 0.0)

    def test_add_zero_left(self):
        bits, value = add_floats(0.0, 2.5)
        self.assertAlmostEqual(value, 2.5, places=5)

    def test_add_zero_right(self):
        bits, value = add_floats(2.5, 0.0)
        self.assertAlmostEqual(value, 2.5, places=5)


class TestFloatSubtraction(unittest.TestCase):

    def test_sub_positive_numbers(self):
        bits, value = sub_floats(5.5, 2.25)
        self.assertEqual(bits[0], POSITIVE_SIGN)
        self.assertAlmostEqual(value, 3.25, places=5)

    def test_sub_negative_result(self):
        bits, value = sub_floats(2.0, 5.0)
        self.assertEqual(bits[0], NEGATIVE_SIGN)
        self.assertAlmostEqual(value, -3.0, places=5)

    def test_sub_negative_and_positive(self):
        bits, value = sub_floats(-2.5, 1.5)
        self.assertEqual(bits[0], NEGATIVE_SIGN)
        self.assertAlmostEqual(value, -4.0, places=5)

    def test_sub_equal_numbers(self):
        bits, value = sub_floats(1.0, 1.0)
        self.assertEqual(bits, [0] * FLOAT_BIT_SIZE)
        self.assertEqual(value, 0.0)


class TestFloatMultiplication(unittest.TestCase):

    def test_mul_positive_numbers(self):
        bits, value = mul_floats(2.0, 4.0)
        self.assertEqual(bits[0], POSITIVE_SIGN)
        self.assertAlmostEqual(value, 8.0, places=5)

    def test_mul_negative_numbers(self):
        bits, value = mul_floats(-2.0, -4.0)
        self.assertEqual(bits[0], POSITIVE_SIGN)
        self.assertAlmostEqual(value, 8.0, places=5)

    def test_mul_mixed_sign_numbers(self):
        bits, value = mul_floats(-2.0, 4.0)
        self.assertEqual(bits[0], NEGATIVE_SIGN)
        self.assertAlmostEqual(value, -8.0, places=5)

    def test_mul_by_zero(self):
        bits, value = mul_floats(5.0, 0.0)
        self.assertEqual(bits, [0] * FLOAT_BIT_SIZE)
        self.assertEqual(value, 0.0)

    def test_mul_zero_and_infinity_returns_nan(self):
        bits, value = mul_floats(0.0, float("inf"))
        self.assertTrue(math.isnan(value))
        self.assertTrue(math.isnan(from_ieee754(bits)))

    def test_mul_infinity(self):
        bits, value = mul_floats(float("inf"), 2.0)
        self.assertEqual(bits[0], POSITIVE_SIGN)
        self.assertEqual(value, float("inf"))

    def test_mul_nan_operand(self):
        bits, value = mul_floats(float("nan"), 1.0)
        self.assertTrue(math.isnan(value))
        self.assertTrue(math.isnan(from_ieee754(bits)))

    def test_mul_negative_infinity(self):
        bits, value = mul_floats(float("-inf"), 2.0)
        self.assertEqual(bits[0], NEGATIVE_SIGN)
        self.assertEqual(value, float("-inf"))

    def test_mul_small_numbers_underflow(self):
        bits, value = mul_floats(1e-30, 1e-20)
        self.assertEqual(bits, [0] * FLOAT_BIT_SIZE)
        self.assertEqual(value, 0.0)

    def test_mul_negative_small_numbers_underflow(self):
        bits, value = mul_floats(-1e-30, 1e-20)
        expected = [NEGATIVE_SIGN] + [0] * (FLOAT_BIT_SIZE - 1)
        self.assertEqual(bits, expected)
        self.assertEqual(value, -0.0)

    def test_mul_large_numbers_overflow(self):
        bits, value = mul_floats(1e20, 1e20)
        self.assertEqual(bits[0], POSITIVE_SIGN)
        self.assertEqual(value, float("inf"))

    def test_mul_negative_large_numbers_overflow(self):
        bits, value = mul_floats(-1e20, 1e20)
        self.assertEqual(bits[0], NEGATIVE_SIGN)
        self.assertEqual(value, float("-inf"))

    def test_mul_requires_rounding(self):
        bits, value = mul_floats(1.4, 1.6)
        self.assertAlmostEqual(value, 2.24, places=4)


class TestFloatDivision(unittest.TestCase):

    def test_div_positive_numbers(self):
        bits, value = div_floats(8.0, 2.0)
        self.assertEqual(bits[0], POSITIVE_SIGN)
        self.assertAlmostEqual(value, 4.0, places=5)

    def test_div_fraction_result(self):
        bits, value = div_floats(7.0, 2.0)
        self.assertAlmostEqual(value, 3.5, places=5)

    def test_div_negative_result(self):
        bits, value = div_floats(-8.0, 2.0)
        self.assertEqual(bits[0], NEGATIVE_SIGN)
        self.assertAlmostEqual(value, -4.0, places=5)

    def test_div_zero_by_number(self):
        bits, value = div_floats(0.0, 2.0)
        self.assertEqual(bits, [0] * FLOAT_BIT_SIZE)
        self.assertEqual(value, 0.0)

    def test_div_by_zero(self):
        bits, value = div_floats(2.0, 0.0)
        self.assertEqual(bits[0], POSITIVE_SIGN)
        self.assertEqual(value, float("inf"))

    def test_div_zero_by_zero(self):
        bits, value = div_floats(0.0, 0.0)
        self.assertTrue(math.isnan(value))
        self.assertTrue(math.isnan(from_ieee754(bits)))

    def test_div_infinity_by_infinity(self):
        bits, value = div_floats(float("inf"), float("inf"))
        self.assertTrue(math.isnan(value))
        self.assertTrue(math.isnan(from_ieee754(bits)))

    def test_div_infinity_by_number(self):
        bits, value = div_floats(float("inf"), 2.0)
        self.assertEqual(bits[0], POSITIVE_SIGN)
        self.assertEqual(value, float("inf"))

    def test_div_number_by_infinity(self):
        bits, value = div_floats(2.0, float("inf"))
        self.assertEqual(bits, [0] * FLOAT_BIT_SIZE)
        self.assertEqual(value, 0.0)

    def test_div_nan(self):
        bits, value = div_floats(float("nan"), 2.0)
        self.assertTrue(math.isnan(value))
        self.assertTrue(math.isnan(from_ieee754(bits)))

if __name__ == '__main__':
    unittest.main()