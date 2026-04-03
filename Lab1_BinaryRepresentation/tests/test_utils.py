import unittest
import sys
import os

from constants import BIT_SIZE

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from utils import (
    add_binary_lists,
    negate_bits,
    multiply_binary_lists,
    delete_leading_zeros,
    int_to_binary_list,
    binary_list_to_int,
    fraction_to_binary_list,
    binary_fraction_to_float,
    invert_bits,
    pad_lists_to_equal_length,
    compare_binary_lists,
    subtract_binary_lists,
)

class TestIntToBinaryList(unittest.TestCase):

    def test_zero(self):
        self.assertEqual(int_to_binary_list(0), [0])

    def test_positive_number(self):
        self.assertEqual(int_to_binary_list(10), [1, 0, 1, 0])


class TestBinaryListToInt(unittest.TestCase):

    def test_zero(self):
        self.assertEqual(binary_list_to_int([0]), 0)

    def test_positive_number(self):
        self.assertEqual(binary_list_to_int([1, 0, 1, 0]), 10)


class TestFractionToBinaryList(unittest.TestCase):

    def test_exact_fraction(self):
        self.assertEqual(fraction_to_binary_list(0.625), [1, 0, 1])

    def test_zero_fraction(self):
        self.assertEqual(fraction_to_binary_list(0.0), [])

    def test_limited_fraction(self):
        self.assertEqual(fraction_to_binary_list(0.1, limit=5), [0, 0, 0, 1, 1])


class TestBinaryFractionToFloat(unittest.TestCase):

    def test_zero(self):
        self.assertEqual(binary_fraction_to_float([0]), 0.0)

    def test_exact_fraction(self):
        self.assertEqual(binary_fraction_to_float([1, 0, 1]), 0.625)


class TestInvertBits(unittest.TestCase):

    def test_invert_bits(self):
        self.assertEqual(invert_bits([1, 0, 1, 1]), [0, 1, 0, 0])


class TestPadListsToEqualLength(unittest.TestCase):

    def test_first_longer(self):
        a, b, max_len = pad_lists_to_equal_length([1, 0, 1], [1])
        self.assertEqual(a, [1, 0, 1])
        self.assertEqual(b, [0, 0, 1])
        self.assertEqual(max_len, 3)

    def test_second_longer(self):
        a, b, max_len = pad_lists_to_equal_length([1], [1, 0, 1])
        self.assertEqual(a, [0, 0, 1])
        self.assertEqual(b, [1, 0, 1])
        self.assertEqual(max_len, 3)

    def test_equal_length(self):
        a, b, max_len = pad_lists_to_equal_length([1, 0], [0, 1])
        self.assertEqual(a, [1, 0])
        self.assertEqual(b, [0, 1])
        self.assertEqual(max_len, 2)


class TestCompareBinaryLists(unittest.TestCase):

    def test_equal(self):
        self.assertEqual(compare_binary_lists([0, 1, 0], [1, 0]), 0)

    def test_first_greater(self):
        self.assertEqual(compare_binary_lists([1, 0, 1], [1, 0]), 1)

    def test_second_greater(self):
        self.assertEqual(compare_binary_lists([1, 0], [1, 1]), -1)


class TestSubtractBinaryLists(unittest.TestCase):

    def test_simple_subtraction(self):
        self.assertEqual(subtract_binary_lists([1, 0, 1], [0, 1, 1]), [1, 0])

    def test_equal_numbers(self):
        self.assertEqual(subtract_binary_lists([1, 0, 1], [1, 0, 1]), [0])

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


class TestNegateBits(unittest.TestCase):

    def test_negate_zero(self):
        """
        Test negating zero: -0 = 0.
        00...00 -> Invert -> 11...11 -> Add 1 -> 100...00 (33 bits).
        Should truncate to 00...00.
        """
        zero_bits = [0] * 32

        result = negate_bits(zero_bits)

        # Result should still be 32 bits of zeros
        expected = [0] * 32
        self.assertEqual(result, expected, "Negating zero should return zero (truncated)")
        self.assertEqual(len(result), 32, "Result should maintain 32-bit width")

    def test_negate_positive(self):
        """Test negating 1"""
        one_bits = [0] * 31 + [1]  # 00...01
        result = negate_bits(one_bits)

        # Expected: 11...11 (-1)
        expected = [1] * 32
        self.assertEqual(result, expected)

class TestMulBinLists(unittest.TestCase):

    def test_both_zeros(self):
        a = [0, 0, 0, 0]
        b = [0, 0]
        result = multiply_binary_lists(a, b)
        expected_result = [0]
        self.assertEqual(result, expected_result)

class TestDeleteLeadZeros(unittest.TestCase):

    def test_list_zeros(self):
        a = [0] * BIT_SIZE
        result = delete_leading_zeros(a)
        expected_result = [0]
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()


