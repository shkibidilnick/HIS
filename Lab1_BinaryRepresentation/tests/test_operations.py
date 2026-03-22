import unittest
import sys
import os

from constants import POSITIVE_SIGN, NEGATIVE_SIGN, MAX_VALUE, MIN_VALUE

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from integer.operations import add_complementary_numbers

class TestIntegerAddition(unittest.TestCase):

    def test_add_positive_numbers(self):
        bits, val, overflow = add_complementary_numbers(10, 5)
        self.assertEqual(val, 15)
        expected_bits = [POSITIVE_SIGN] + [0] * (len(bits) - 1 - 4) + [1, 1, 1, 1]
        self.assertEqual(bits, expected_bits)
        self.assertFalse(overflow, "Should not overflow")

    def test_add_negative_numbers(self):
        bits, val, overflow = add_complementary_numbers(-10, -5)
        self.assertEqual(val, -15)
        expected_bits = [NEGATIVE_SIGN] + [1] * (len(bits) - 1 - 4) + [0, 0, 0, 1]
        self.assertEqual(bits, expected_bits)
        self.assertFalse(overflow, "Should not overflow")

    def test_add_mixed_numbers(self):
        bits, val, overflow = add_complementary_numbers(10, -5)
        self.assertEqual(val, 5)
        expected_bits = [POSITIVE_SIGN] + [0] * (len(bits) - 1 - 3) + [1, 0, 1]
        self.assertEqual(bits, expected_bits)
        self.assertFalse(overflow, "Should not overflow")

    def test_positive_overflow_detection(self):
        """
        Test MAX + 1. Result wraps to MIN, but Overflow Flag should be True.
        """
        bits, val, overflow = add_complementary_numbers(MAX_VALUE, 1)
        expected_wrapped_value = MIN_VALUE
        self.assertEqual(val, expected_wrapped_value, "Value should wrap to MIN")
        self.assertTrue(overflow, "Overflow flag should be raised for MAX + 1")

    def test_negative_overflow_detection(self):
        """
        Test MIN + (-1). Result wraps
        """
        bits, val, overflow = add_complementary_numbers(MIN_VALUE, -1)
        expected_wrapped_value = MAX_VALUE
        self.assertEqual(val, expected_wrapped_value, "Value should be wrap to MAX")
        self.assertTrue(overflow, "Overflow flag should be raised for MIN - 1")

if __name__ == '__main__':
    unittest.main()


