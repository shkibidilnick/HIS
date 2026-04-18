from typing import List, Tuple

from constants import (
    FLOAT_EXP_BITS,
    FLOAT_MANTISSA_BITS,
    FLOAT_SIGNIFICAND_BITS,
    POSITIVE_SIGN,
    IEEE_FLOAT_EXP_LIMIT,
    FLOAT_BIAS,
)
from utils import (
    multiply_binary_lists,
    binary_list_to_int,
    int_to_binary_list,
)
from floating_point.converter import to_ieee754, from_ieee754


def _build_nan_bits() -> List[int]:
    return [POSITIVE_SIGN] + [1] * FLOAT_EXP_BITS + [1] + [0] * (FLOAT_MANTISSA_BITS - 1)


def _build_zero_bits(sign_bit: int) -> List[int]:
    return [sign_bit] + [0] * (FLOAT_EXP_BITS + FLOAT_MANTISSA_BITS)


def _build_infinity_bits(sign_bit: int) -> List[int]:
    return [sign_bit] + [1] * FLOAT_EXP_BITS + [0] * FLOAT_MANTISSA_BITS


def _pad_left(bits: List[int], target_size: int) -> List[int]:
    if len(bits) >= target_size:
        return bits[:]
    return [0] * (target_size - len(bits)) + bits


def _is_zero(exponent_value: int, mantissa_value: int) -> bool:
    return exponent_value == 0 and mantissa_value == 0


def _is_infinity(exponent_value: int, mantissa_value: int) -> bool:
    return exponent_value == IEEE_FLOAT_EXP_LIMIT and mantissa_value == 0


def _is_nan(exponent_value: int, mantissa_value: int) -> bool:
    return exponent_value == IEEE_FLOAT_EXP_LIMIT and mantissa_value != 0


def _parse_float(decimal_value: float) -> Tuple[List[int], int, int, int, int]:
    bits = to_ieee754(decimal_value)
    sign_bit = bits[0]
    exponent_bits = bits[1:1 + FLOAT_EXP_BITS]
    mantissa_bits = bits[1 + FLOAT_EXP_BITS:]

    exponent_value = binary_list_to_int(exponent_bits)
    mantissa_value = binary_list_to_int(mantissa_bits)

    return bits, sign_bit, exponent_value, mantissa_value, binary_list_to_int([1] + mantissa_bits)


def _assemble_result(
    sign_bit: int,
    exponent_value: int,
    significand_value: int,
) -> Tuple[List[int], float]:
    if significand_value == 0:
        result_bits = _build_zero_bits(sign_bit)
        return result_bits, from_ieee754(result_bits)

    while significand_value >= (1 << FLOAT_SIGNIFICAND_BITS):
        significand_value >>= 1
        exponent_value += 1

    while significand_value < (1 << (FLOAT_SIGNIFICAND_BITS - 1)) and exponent_value > 0:
        significand_value <<= 1
        exponent_value -= 1

    if exponent_value >= IEEE_FLOAT_EXP_LIMIT:
        result_bits = _build_infinity_bits(sign_bit)
        return result_bits, from_ieee754(result_bits)

    if exponent_value <= 0:
        result_bits = _build_zero_bits(sign_bit)
        return result_bits, from_ieee754(result_bits)

    mantissa_value = significand_value - (1 << (FLOAT_SIGNIFICAND_BITS - 1))
    exponent_bits = _pad_left(int_to_binary_list(exponent_value), FLOAT_EXP_BITS)
    mantissa_bits = _pad_left(int_to_binary_list(mantissa_value), FLOAT_MANTISSA_BITS)

    if len(mantissa_bits) > FLOAT_MANTISSA_BITS:
        mantissa_bits = mantissa_bits[-FLOAT_MANTISSA_BITS:]

    result_bits = [sign_bit] + exponent_bits + mantissa_bits
    return result_bits, from_ieee754(result_bits)


def add_floats(a_decimal: float, b_decimal: float) -> Tuple[List[int], float]:
    a_bits, sign_a, exp_a, mantissa_a, significand_a = _parse_float(a_decimal)
    b_bits, sign_b, exp_b, mantissa_b, significand_b = _parse_float(b_decimal)

    if _is_nan(exp_a, mantissa_a) or _is_nan(exp_b, mantissa_b):
        result_bits = _build_nan_bits()
        return result_bits, from_ieee754(result_bits)

    if _is_infinity(exp_a, mantissa_a) and _is_infinity(exp_b, mantissa_b):
        if sign_a != sign_b:
            result_bits = _build_nan_bits()
            return result_bits, from_ieee754(result_bits)

        result_bits = _build_infinity_bits(sign_a)
        return result_bits, from_ieee754(result_bits)

    if _is_infinity(exp_a, mantissa_a):
        return a_bits, from_ieee754(a_bits)

    if _is_infinity(exp_b, mantissa_b):
        return b_bits, from_ieee754(b_bits)

    if _is_zero(exp_a, mantissa_a) and _is_zero(exp_b, mantissa_b):
        result_bits = _build_zero_bits(POSITIVE_SIGN)
        return result_bits, from_ieee754(result_bits)

    if _is_zero(exp_a, mantissa_a):
        return b_bits, from_ieee754(b_bits)

    if _is_zero(exp_b, mantissa_b):
        return a_bits, from_ieee754(a_bits)

    target_exponent = max(exp_a, exp_b)
    aligned_significand_a = significand_a >> (target_exponent - exp_a)
    aligned_significand_b = significand_b >> (target_exponent - exp_b)

    if sign_a == sign_b:
        result_sign = sign_a
        result_significand = aligned_significand_a + aligned_significand_b
    else:
        if aligned_significand_a == aligned_significand_b:
            result_bits = _build_zero_bits(POSITIVE_SIGN)
            return result_bits, from_ieee754(result_bits)

        if aligned_significand_a > aligned_significand_b:
            result_sign = sign_a
            result_significand = aligned_significand_a - aligned_significand_b
        else:
            result_sign = sign_b
            result_significand = aligned_significand_b - aligned_significand_a

    return _assemble_result(result_sign, target_exponent, result_significand)


def sub_floats(a_decimal: float, b_decimal: float) -> Tuple[List[int], float]:
    return add_floats(a_decimal, -b_decimal)


def mul_floats(a_decimal: float, b_decimal: float) -> Tuple[List[int], float]:
    _, sign_a, exp_a, mantissa_a, significand_a = _parse_float(a_decimal)
    _, sign_b, exp_b, mantissa_b, significand_b = _parse_float(b_decimal)

    if _is_nan(exp_a, mantissa_a) or _is_nan(exp_b, mantissa_b):
        result_bits = _build_nan_bits()
        return result_bits, from_ieee754(result_bits)

    result_sign = sign_a ^ sign_b

    if (_is_zero(exp_a, mantissa_a) and _is_infinity(exp_b, mantissa_b)) or (
        _is_zero(exp_b, mantissa_b) and _is_infinity(exp_a, mantissa_a)
    ):
        result_bits = _build_nan_bits()
        return result_bits, from_ieee754(result_bits)

    if _is_zero(exp_a, mantissa_a) or _is_zero(exp_b, mantissa_b):
        result_bits = _build_zero_bits(result_sign)
        return result_bits, from_ieee754(result_bits)

    if _is_infinity(exp_a, mantissa_a) or _is_infinity(exp_b, mantissa_b):
        result_bits = _build_infinity_bits(result_sign)
        return result_bits, from_ieee754(result_bits)

    product_bits = multiply_binary_lists(
        int_to_binary_list(significand_a),
        int_to_binary_list(significand_b),
    )
    product_value = binary_list_to_int(product_bits)

    round_bit = (product_value >> (FLOAT_MANTISSA_BITS - 1)) & 1
    significand_value = product_value >> FLOAT_MANTISSA_BITS
    if round_bit == 1:
        significand_value += 1

    result_exponent = exp_a + exp_b - FLOAT_BIAS

    return _assemble_result(result_sign, result_exponent, significand_value)


def div_floats(a_decimal: float, b_decimal: float) -> Tuple[List[int], float]:
    _, sign_a, exp_a, mantissa_a, significand_a = _parse_float(a_decimal)
    _, sign_b, exp_b, mantissa_b, significand_b = _parse_float(b_decimal)

    if _is_nan(exp_a, mantissa_a) or _is_nan(exp_b, mantissa_b):
        result_bits = _build_nan_bits()
        return result_bits, from_ieee754(result_bits)

    if _is_infinity(exp_a, mantissa_a) and _is_infinity(exp_b, mantissa_b):
        result_bits = _build_nan_bits()
        return result_bits, from_ieee754(result_bits)

    if _is_zero(exp_a, mantissa_a) and _is_zero(exp_b, mantissa_b):
        result_bits = _build_nan_bits()
        return result_bits, from_ieee754(result_bits)

    result_sign = sign_a ^ sign_b

    if _is_zero(exp_b, mantissa_b):
        result_bits = _build_infinity_bits(result_sign)
        return result_bits, from_ieee754(result_bits)

    if _is_zero(exp_a, mantissa_a):
        result_bits = _build_zero_bits(result_sign)
        return result_bits, from_ieee754(result_bits)

    if _is_infinity(exp_a, mantissa_a):
        result_bits = _build_infinity_bits(result_sign)
        return result_bits, from_ieee754(result_bits)

    if _is_infinity(exp_b, mantissa_b):
        result_bits = _build_zero_bits(result_sign)
        return result_bits, from_ieee754(result_bits)

    scaled_dividend = significand_a << FLOAT_MANTISSA_BITS
    quotient_value = scaled_dividend // significand_b

    result_exponent = exp_a - exp_b + FLOAT_BIAS

    return _assemble_result(result_sign, result_exponent, quotient_value)