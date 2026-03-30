from typing import List, Tuple

from integer.converter import to_direct_code, from_direct_code
from src.constants import BIT_SIZE
from src.utils import add_binary_lists, multiply_binary_lists, negate_bits, delete_leading_zeros
from src.integer.converter import to_complementary_code, from_complementary_code


def _add_bits_core(a_bits: List[int], b_bits: List[int]) -> Tuple[List[int], bool]:
    """
    Internal core function.
    Performs raw binary addition of two 32-bit arrays.
    Detects overflow based on operand signs.

    Returns:
        Tuple: (result_bits, is_overflow)
    """
    raw_result = add_binary_lists(a_bits, b_bits)

    if len(raw_result) > BIT_SIZE:
        result_bits = raw_result[-BIT_SIZE:]
    else:
        result_bits = raw_result

    sign_a = a_bits[0]
    sign_b = b_bits[0]
    sign_res = result_bits[0]
    is_overflow = (sign_a == sign_b) and (sign_res != sign_a)

    return result_bits, is_overflow

def add_complementary_numbers(a_decimal: int, b_decimal: int) -> Tuple[List[int], int, bool]:
    """
    Public API for Addition.
    Converts inputs to bits, calls core logic, converts back.
    """
    a_bits = to_complementary_code(a_decimal)
    b_bits = to_complementary_code(b_decimal)

    result_bits, is_overflow = _add_bits_core(a_bits, b_bits)
    result_decimal = from_complementary_code(result_bits)

    return result_bits, result_decimal, is_overflow

def subtract_complementary_bits(a_bits: List[int], b_bits: List[int]) -> Tuple[List[int], int, bool]:
    """
    Public API for Subtraction.
    Implements A - B as A + (-B).
    """
    neg_b_bits = negate_bits(b_bits)
    result_bits, is_overflow = _add_bits_core(a_bits, neg_b_bits)
    result_decimal = from_complementary_code(result_bits)
    return result_bits, result_decimal, is_overflow

def multiply_direct_numbers(a_decimal: int, b_decimal: int) -> Tuple[List[int], int, bool]:

    if a_decimal == 0 or b_decimal == 0:
        zero_bits = [0] * BIT_SIZE
        return zero_bits, 0, False

    a_direct = to_direct_code(a_decimal)
    b_direct = to_direct_code(b_decimal)

    # 0 ^ 0 = 0, 1 ^ 1 = 1, 0 ^ 1 = 1, 1 ^ 0 = 1
    result_sign = a_direct[0] ^ b_direct[0]

    # module for number, ex. 100..0101 -> 00..0101
    a_mod_raw = a_direct[1:]
    b_mod_raw = b_direct[1:]

    # cut module, ex. 00..0101 -> 101
    a_mod = delete_leading_zeros(a_mod_raw)
    b_mod = delete_leading_zeros(b_mod_raw)

    result_mod = multiply_binary_lists(a_mod, b_mod)
    max_mod_bits = BIT_SIZE -1
    is_overflow = False

    if len(result_mod) > max_mod_bits:
        is_overflow = True
        result_mod = result_mod[-max_mod_bits:]
    else:
        padding = max_mod_bits - len(result_mod)
        result_mod = [0] * padding + result_mod

    result_bits = [result_sign] + result_mod
    result_decimal = from_direct_code(result_bits)

    return result_bits, result_decimal, is_overflow