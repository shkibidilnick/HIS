import math
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from constants import (
    POSITIVE_SIGN,
    NEGATIVE_SIGN,
    FLOAT_BIT_SIZE,
    FLOAT_EXP_BITS,
    FLOAT_MANTISSA_BITS,
)
from floating_point.converter import (
    to_ieee754,
    from_ieee754,
    _build_zero_bits,
    _build_infinity_bits,
    _build_nan_bits,
    _pad_left,
)


class TestFloatConverterHelpers(unittest.TestCase):

    def test_build_zero_bits_positive(self):
        expected = [POSITIVE_SIGN] + [0] * (FLOAT_BIT_SIZE - 1)
        self.assertEqual(_build_zero_bits(POSITIVE_SIGN), expected)

    def test_build_zero_bits_negative(self):
        expected = [NEGATIVE_SIGN] + [0] * (FLOAT_BIT_SIZE - 1)
        self.assertEqual(_build_zero_bits(NEGATIVE_SIGN), expected)

    def test_build_infinity_bits(self):
        bits = _build_infinity_bits(NEGATIVE_SIGN)

        self.assertEqual(bits[0], NEGATIVE_SIGN)
        self.assertEqual(bits[1:1 + FLOAT_EXP_BITS], [1] * FLOAT_EXP_BITS)
        self.assertEqual(bits[1 + FLOAT_EXP_BITS:], [0] * FLOAT_MANTISSA_BITS)

    def test_build_nan_bits(self):
        bits = _build_nan_bits()

        self.assertEqual(bits[0], POSITIVE_SIGN)
        self.assertEqual(bits[1:1 + FLOAT_EXP_BITS], [1] * FLOAT_EXP_BITS)
        self.assertTrue(any(bit == 1 for bit in bits[1 + FLOAT_EXP_BITS:]))

    def test_pad_left_without_padding(self):
        self.assertEqual(_pad_left([1, 0, 1], 3), [1, 0, 1])

    def test_pad_left_with_padding(self):
        self.assertEqual(_pad_left([1, 0, 1], 5), [0, 0, 1, 0, 1])


class TestFloatConverter(unittest.TestCase):

    def test_zero(self):
        bits = to_ieee754(0.0)
        expected = [0] * FLOAT_BIT_SIZE
        self.assertEqual(bits, expected)
        self.assertEqual(from_ieee754(bits), 0.0)

    def test_negative_zero(self):
        bits = to_ieee754(-0.0)
        expected = [NEGATIVE_SIGN] + [0] * (FLOAT_BIT_SIZE - 1)
        self.assertEqual(bits, expected)
        self.assertEqual(from_ieee754(bits), -0.0)

    def test_one(self):
        bits = to_ieee754(1.0)

        self.assertEqual(bits[0], POSITIVE_SIGN)
        self.assertEqual(bits[1:9], [0, 1, 1, 1, 1, 1, 1, 1])
        self.assertEqual(bits[9:], [0] * FLOAT_MANTISSA_BITS)
        self.assertEqual(from_ieee754(bits), 1.0)

    def test_negative_five(self):
        bits = to_ieee754(-5.0)

        self.assertEqual(bits[0], NEGATIVE_SIGN)
        self.assertEqual(bits[1:9], [1, 0, 0, 0, 0, 0, 0, 1])
        self.assertEqual(bits[9:11], [0, 1])
        self.assertEqual(bits[11:], [0] * (FLOAT_MANTISSA_BITS - 2))
        self.assertEqual(from_ieee754(bits), -5.0)

    def test_fraction_complex(self):
        bits = to_ieee754(0.625)

        self.assertEqual(bits[0], POSITIVE_SIGN)
        self.assertEqual(bits[1:9], [0, 1, 1, 1, 1, 1, 1, 0])
        self.assertEqual(bits[9:11], [0, 1])
        self.assertEqual(bits[11:], [0] * (FLOAT_MANTISSA_BITS - 2))
        self.assertEqual(from_ieee754(bits), 0.625)

    def test_combined_number(self):
        bits = to_ieee754(-13.625)

        self.assertEqual(bits[0], NEGATIVE_SIGN)
        self.assertEqual(bits[1:9], [1, 0, 0, 0, 0, 0, 1, 0])
        self.assertEqual(bits[9:15], [1, 0, 1, 1, 0, 1])
        self.assertEqual(bits[15:], [0] * (FLOAT_MANTISSA_BITS - 6))
        self.assertEqual(from_ieee754(bits), -13.625)

    def test_overflow_to_infinity(self):
        bits = to_ieee754(1e40)

        self.assertEqual(bits[0], POSITIVE_SIGN)
        self.assertEqual(bits[1:9], [1] * FLOAT_EXP_BITS)
        self.assertEqual(bits[9:], [0] * FLOAT_MANTISSA_BITS)
        self.assertEqual(from_ieee754(bits), float("inf"))

    def test_underflow_to_zero(self):
        bits = to_ieee754(2.0 ** -130)

        expected = [0] * FLOAT_BIT_SIZE
        self.assertEqual(bits, expected)
        self.assertEqual(from_ieee754(bits), 0.0)

    def test_negative_underflow_to_zero(self):
        bits = to_ieee754(-(2.0 ** -130))

        expected = [NEGATIVE_SIGN] + [0] * (FLOAT_BIT_SIZE - 1)
        self.assertEqual(bits, expected)
        self.assertEqual(from_ieee754(bits), -0.0)

    def test_nan_parsing(self):
        nan_bits = [0] + [1] * FLOAT_EXP_BITS + [1] + [0] * (FLOAT_MANTISSA_BITS - 1)
        self.assertTrue(math.isnan(from_ieee754(nan_bits)))

    def test_long_mantissa_truncation(self):
        bits = to_ieee754(1.2)
        result = from_ieee754(bits)
        self.assertAlmostEqual(result, 1.2, places=5)

    def test_positive_infinity_to_bits(self):
        bits = to_ieee754(float("inf"))

        self.assertEqual(bits[0], POSITIVE_SIGN)
        self.assertEqual(bits[1:9], [1] * FLOAT_EXP_BITS)
        self.assertEqual(bits[9:], [0] * FLOAT_MANTISSA_BITS)

    def test_negative_infinity_to_bits(self):
        bits = to_ieee754(float("-inf"))

        self.assertEqual(bits[0], NEGATIVE_SIGN)
        self.assertEqual(bits[1:9], [1] * FLOAT_EXP_BITS)
        self.assertEqual(bits[9:], [0] * FLOAT_MANTISSA_BITS)

    def test_nan_to_bits(self):
        bits = to_ieee754(float("nan"))

        self.assertEqual(bits[0], POSITIVE_SIGN)
        self.assertEqual(bits[1:9], [1] * FLOAT_EXP_BITS)
        self.assertTrue(any(bit == 1 for bit in bits[9:]))

    def test_negative_zero_from_bits(self):
        bits = [NEGATIVE_SIGN] + [0] * (FLOAT_BIT_SIZE - 1)
        self.assertEqual(from_ieee754(bits), -0.0)

if __name__ == '__main__':
    unittest.main()