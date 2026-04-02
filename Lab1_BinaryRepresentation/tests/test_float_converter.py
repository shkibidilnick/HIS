import unittest
import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from floating_point.converter import to_ieee754, from_ieee754
from constants import POSITIVE_SIGN, NEGATIVE_SIGN, FLOAT_BIT_SIZE, FLOAT_MANTISSA_BITS

class TestFloatConverter(unittest.TestCase):

    def test_zero(self):
        bits = to_ieee754(0.0)
        expected = [0] * FLOAT_BIT_SIZE
        self.assertEqual(bits, expected)

        val = from_ieee754(bits)
        self.assertEqual(val ,0.0)

    def test_one(self):
        bits = to_ieee754(1.0)

        self.assertEqual(bits[0], POSITIVE_SIGN)
        expected_exp = [0, 1, 1, 1, 1, 1, 1, 1]
        self.assertEqual(bits[1:9], expected_exp)
        self.assertEqual(bits[9:], [0] * FLOAT_MANTISSA_BITS)

        self.assertEqual(from_ieee754(bits), 1.0)

    def test_negative_five(self):
        """-5.0 -> -1.01 * 2^2"""
        bits = to_ieee754(-5.0)

        self.assertEqual(bits[0], NEGATIVE_SIGN)
        expected_exp = [1, 0, 0, 0, 0, 0, 0, 1]
        self.assertEqual(bits[1:9], expected_exp)
        self.assertEqual(bits[9:11], [0, 1])
        self.assertEqual(bits[11:], [0] * (FLOAT_MANTISSA_BITS - 2))

        self.assertEqual(from_ieee754(bits), -5.0)

    def test_fraction_complex(self):
        """0.625 -> 1.01 * 2^-1"""
        bits = to_ieee754(0.625)

        self.assertEqual(bits[0], POSITIVE_SIGN)
        expected_exp = [0, 1, 1, 1, 1, 1, 1, 0]
        self.assertEqual(bits[1:9], expected_exp)
        self.assertEqual(bits[9:11], [0, 1])
        self.assertEqual(bits[11:], [0] * (FLOAT_MANTISSA_BITS - 2))

        self.assertEqual(from_ieee754(bits), 0.625)

    def test_combined_number(self):
        """-13.625 -> -1101.101 -> 1.101101 * 2^3"""
        bits = to_ieee754(-13.625)

        self.assertEqual(bits[0], NEGATIVE_SIGN)
        expected_exp = [1, 0, 0, 0, 0, 0, 1, 0]
        self.assertEqual(bits[1:9], expected_exp)
        self.assertEqual(bits[9:15], [1, 0, 1, 1, 0, 1])
        self.assertEqual(bits[15:], [0] * (FLOAT_MANTISSA_BITS - 6))

        self.assertEqual(from_ieee754(bits), -13.625)

    def overflow_to_infinity(self):
        bits = to_ieee754(1e40)

        self.assertEqual(bits[0], POSITIVE_SIGN)
        self.assertEqual(bits[1:9], [1] * 8)
        self.assertEqual(bits[9:], [0] * 23)

        result = from_ieee754(bits)
        self.assertEqual(result, float('inf'))

    def test_underflow_to_zero(self):
        bits = to_ieee754(1e-50)

        expected = [0] * 32
        self.assertEqual(bits, expected)

        result = from_ieee754(bits)
        self.assertEqual(result, 0.0)

    def test_nan_parsing(self):
        nan_bits = [0] + [1] * 8 + [1] + [0] * 22

        result = from_ieee754(nan_bits)
        self.assertTrue(math.isnan(result))

    def test_long_mantissa_truncation(self):
        val = 1.2
        bits = to_ieee754(val)
        result = from_ieee754(bits)

        self.assertAlmostEqual(result, 1.2, places=5)

if __name__ == '__main__':
    unittest.main()

