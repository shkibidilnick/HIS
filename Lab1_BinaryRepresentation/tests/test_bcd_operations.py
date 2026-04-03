import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from bcd.converter import digit_to_5421_bcd
from bcd.operations import (
    _add_decimal_digits,
    _add_5421_tetrads,
    add_5421_bcd_numbers,
)


class TestBcd5421OperationsHelpers(unittest.TestCase):

    def test_add_decimal_digits_without_carry(self):
        result_digit, carry = _add_decimal_digits(2, 3, 0)
        self.assertEqual(result_digit, 5)
        self.assertEqual(carry, 0)

    def test_add_decimal_digits_with_carry_out(self):
        result_digit, carry = _add_decimal_digits(7, 5, 0)
        self.assertEqual(result_digit, 2)
        self.assertEqual(carry, 1)

    def test_add_decimal_digits_with_carry_in(self):
        result_digit, carry = _add_decimal_digits(4, 5, 1)
        self.assertEqual(result_digit, 0)
        self.assertEqual(carry, 1)

    def test_add_5421_tetrads_without_carry(self):
        result_tetrad, carry = _add_5421_tetrads(
            digit_to_5421_bcd(2),
            digit_to_5421_bcd(3),
            0,
        )
        self.assertEqual(result_tetrad, digit_to_5421_bcd(5))
        self.assertEqual(carry, 0)

    def test_add_5421_tetrads_with_carry(self):
        result_tetrad, carry = _add_5421_tetrads(
            digit_to_5421_bcd(8),
            digit_to_5421_bcd(7),
            0,
        )
        self.assertEqual(result_tetrad, digit_to_5421_bcd(5))
        self.assertEqual(carry, 1)


class TestBcd5421Addition(unittest.TestCase):

    def test_add_single_digits(self):
        result_tetrads, result_decimal = add_5421_bcd_numbers(2, 3)
        self.assertEqual(result_decimal, 5)
        self.assertEqual(result_tetrads, [digit_to_5421_bcd(5)])

    def test_add_single_digits_with_carry(self):
        result_tetrads, result_decimal = add_5421_bcd_numbers(5, 5)
        self.assertEqual(result_decimal, 10)
        self.assertEqual(
            result_tetrads,
            [
                digit_to_5421_bcd(1),
                digit_to_5421_bcd(0),
            ],
        )

    def test_add_multi_digit_numbers(self):
        result_tetrads, result_decimal = add_5421_bcd_numbers(19, 24)
        self.assertEqual(result_decimal, 43)
        self.assertEqual(
            result_tetrads,
            [
                digit_to_5421_bcd(4),
                digit_to_5421_bcd(3),
            ],
        )

    def test_add_with_padding(self):
        result_tetrads, result_decimal = add_5421_bcd_numbers(7, 15)
        self.assertEqual(result_decimal, 22)
        self.assertEqual(
            result_tetrads,
            [
                digit_to_5421_bcd(2),
                digit_to_5421_bcd(2),
            ],
        )

    def test_add_many_carries(self):
        result_tetrads, result_decimal = add_5421_bcd_numbers(99, 1)
        self.assertEqual(result_decimal, 100)
        self.assertEqual(
            result_tetrads,
            [
                digit_to_5421_bcd(1),
                digit_to_5421_bcd(0),
                digit_to_5421_bcd(0),
            ],
        )

    def test_add_zero_and_zero(self):
        result_tetrads, result_decimal = add_5421_bcd_numbers(0, 0)
        self.assertEqual(result_decimal, 0)
        self.assertEqual(result_tetrads, [digit_to_5421_bcd(0)])

    def test_add_zero_and_number(self):
        result_tetrads, result_decimal = add_5421_bcd_numbers(0, 42)
        self.assertEqual(result_decimal, 42)
        self.assertEqual(
            result_tetrads,
            [
                digit_to_5421_bcd(4),
                digit_to_5421_bcd(2),
            ],
        )

    def test_add_negative_number(self):
        with self.assertRaises(ValueError):
            add_5421_bcd_numbers(-1, 5)


if __name__ == "__main__":
    unittest.main()