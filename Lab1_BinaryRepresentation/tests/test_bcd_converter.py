import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from bcd.converter import (
    BCD_5421_DIGIT_MAP,
    digit_to_5421_bcd,
    bcd_5421_to_digit,
    decimal_to_5421_bcd,
    bcd_5421_to_decimal,
)


class TestBcd5421Converter(unittest.TestCase):

    def test_digit_zero(self):
        self.assertEqual(digit_to_5421_bcd(0), [0, 0, 0, 0])

    def test_digit_five(self):
        self.assertEqual(digit_to_5421_bcd(5), [1, 0, 0, 0])

    def test_digit_nine(self):
        self.assertEqual(digit_to_5421_bcd(9), [1, 1, 0, 0])

    def test_digit_out_of_range(self):
        with self.assertRaises(ValueError):
            digit_to_5421_bcd(10)

    def test_bcd_to_digit_zero(self):
        self.assertEqual(bcd_5421_to_digit([0, 0, 0, 0]), 0)

    def test_bcd_to_digit_eight(self):
        self.assertEqual(bcd_5421_to_digit([1, 0, 1, 1]), 8)

    def test_bcd_invalid_tetrad_length(self):
        with self.assertRaises(ValueError):
            bcd_5421_to_digit([1, 0, 1])

    def test_bcd_invalid_tetrad_value(self):
        with self.assertRaises(ValueError):
            bcd_5421_to_digit([1, 1, 1, 1])

    def test_decimal_to_bcd_single_digit(self):
        self.assertEqual(decimal_to_5421_bcd(7), [[1, 0, 1, 0]])

    def test_decimal_to_bcd_multiple_digits(self):
        expected = [
            [0, 1, 0, 0],
            [0, 0, 1, 0],
        ]
        self.assertEqual(decimal_to_5421_bcd(42), expected)

    def test_decimal_to_bcd_zero(self):
        self.assertEqual(decimal_to_5421_bcd(0), [[0, 0, 0, 0]])

    def test_decimal_to_bcd_negative_number(self):
        with self.assertRaises(ValueError):
            decimal_to_5421_bcd(-1)

    def test_bcd_to_decimal_single_tetrad(self):
        self.assertEqual(bcd_5421_to_decimal([[1, 0, 0, 1]]), 6)

    def test_bcd_to_decimal_multiple_tetrads(self):
        tetrads = [
            [0, 0, 0, 1],
            [1, 1, 0, 0],
        ]
        self.assertEqual(bcd_5421_to_decimal(tetrads), 19)

    def test_bcd_to_decimal_empty(self):
        with self.assertRaises(ValueError):
            bcd_5421_to_decimal([])

    def test_all_map_entries_round_trip(self):
        for digit, bits in BCD_5421_DIGIT_MAP.items():
            self.assertEqual(bcd_5421_to_digit(bits), digit)


if __name__ == "__main__":
    unittest.main()