from typing import List, Tuple
from src.constants import BIT_SIZE
from src.utils import add_binary_lists
from src.integer.converter import to_complementary_code, from_complementary_code
from utils import negate_bits


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

def subtract_complementary_bits(a_bits: List[int], b_bits: List[int]) -> Tuple[List[int], bool]:
    """
    Public API for Subtraction.
    Implements A - B as A + (-B).
    """
    neg_b_bits = negate_bits(b_bits)
    return _add_bits_core(a_bits, neg_b_bits)



