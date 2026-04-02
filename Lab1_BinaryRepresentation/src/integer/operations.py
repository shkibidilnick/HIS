from typing import List, Tuple

from constants import NEGATIVE_SIGN
from integer.converter import to_direct_code, from_direct_code, to_complementary_code, from_complementary_code
from src.constants import POSITIVE_SIGN, BIT_SIZE, FRACTIONAL_BITS_REQUIRED
from src.utils import add_binary_lists, multiply_binary_lists, negate_bits, delete_leading_zeros, compare_binary_lists, subtract_binary_lists, binary_list_to_int, binary_fraction_to_float



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
    a_mod = a_direct[1:]
    b_mod = b_direct[1:]

    # cut module, ex. 00..0101 -> 101
    a_clean = delete_leading_zeros(a_mod)
    b_clean = delete_leading_zeros(b_mod)

    result_mod = multiply_binary_lists(a_clean, b_clean)
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

def divide_direct_numbers(a_decimal: int, b_decimal: int) -> Tuple[List[int], List[int], int, float]:
    """
    Performs division using the Restoring Remainder method (Corner Division).
    1. Take current Remainder R.
    2. Append next bit of Divisor -> R_new.
    3. Compare R_new with Divisor D.
    """

    if b_decimal == 0:
        raise ZeroDivisionError("Division by zero")
    if a_decimal == 0:
        return [0] * BIT_SIZE, [0], POSITIVE_SIGN, 0.0

    a_direct = to_direct_code(a_decimal)
    b_direct = to_direct_code(b_decimal)
    result_sign = a_direct[0] ^ b_direct[0]

    dividend_bits = delete_leading_zeros(a_direct[1:])
    divisor_bits = delete_leading_zeros(b_direct[1:])

    remainder = []
    int_part_bits = [] # bits for integer part of the result

    for bit in dividend_bits:
        current_val = remainder + [bit]
        cmp = compare_binary_lists(current_val, divisor_bits)

        if cmp >= 0:
            int_part_bits.append(1)
            remainder = subtract_binary_lists(current_val, divisor_bits)
        else:
            int_part_bits.append(0)
            remainder = current_val

    int_part_bits = delete_leading_zeros(int_part_bits)
    if not int_part_bits: int_part_bits = [0]

    frac_part_bits = [] # bits for float part of the result

    for _ in range(FRACTIONAL_BITS_REQUIRED):
        if not remainder or all(b == 0 for b in remainder):
            break

        current_val = remainder + [0]
        cmp = compare_binary_lists(current_val, divisor_bits)

        if cmp >= 0:
            frac_part_bits.append(1)
            remainder = subtract_binary_lists(current_val, divisor_bits)
        else:
            frac_part_bits.append(0)
            remainder = current_val

    if not frac_part_bits: frac_part_bits = [0]

    int_part_padded = [0] * (BIT_SIZE - 1 - len(int_part_bits)) + int_part_bits
    result_bits = [result_sign] + int_part_padded

    int_val = binary_list_to_int(int_part_bits)
    frac_val = binary_fraction_to_float(frac_part_bits)

    final_decimal = int_val + frac_val
    if result_sign == NEGATIVE_SIGN:
        final_decimal = -final_decimal

    return result_bits, frac_part_bits, result_sign, final_decimal


