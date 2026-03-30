import unittest
import sys
import os

from constants import BIT_SIZE

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from utils import add_binary_lists, negate_bits, multiply_binary_lists, delete_leading_zeros


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


