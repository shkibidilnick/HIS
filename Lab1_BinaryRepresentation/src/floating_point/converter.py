from typing import List
import math

from constants import (
    FLOAT_EXP_BITS,
    FLOAT_MANTISSA_BITS,
    FLOAT_BIAS,
    POSITIVE_SIGN,
    NEGATIVE_SIGN,
    IEEE_FLOAT_EXP_LIMIT,
)
from utils import (
    int_to_binary_list,
    fraction_to_binary_list,
    binary_list_to_int,
    binary_fraction_to_float,
)


def _build_zero_bits(sign_bit: int) -> List[int]:
    return [sign_bit] + [0] * (FLOAT_EXP_BITS + FLOAT_MANTISSA_BITS)


def _build_infinity_bits(sign_bit: int) -> List[int]:
    return [sign_bit] + [1] * FLOAT_EXP_BITS + [0] * FLOAT_MANTISSA_BITS


def _build_nan_bits() -> List[int]:
    return [POSITIVE_SIGN] + [1] * FLOAT_EXP_BITS + [1] + [0] * (FLOAT_MANTISSA_BITS - 1)


def _pad_left(bits: List[int], target_size: int) -> List[int]:
    if len(bits) >= target_size:
        return bits[:]
    return [0] * (target_size - len(bits)) + bits


def to_ieee754(decimal_float: float) -> List[int]:
    if math.isnan(decimal_float):
        return _build_nan_bits()

    if math.isinf(decimal_float):
        sign_bit = NEGATIVE_SIGN if decimal_float < 0 else POSITIVE_SIGN
        return _build_infinity_bits(sign_bit)

    if decimal_float == 0.0:
        sign_bit = NEGATIVE_SIGN if math.copysign(1.0, decimal_float) < 0 else POSITIVE_SIGN
        return _build_zero_bits(sign_bit)

    sign_bit = NEGATIVE_SIGN if decimal_float < 0 else POSITIVE_SIGN
    absolute_value = abs(decimal_float)

    integer_part = int(absolute_value)
    fractional_part = absolute_value - integer_part

    integer_bits = int_to_binary_list(integer_part)
    fractional_bits = fraction_to_binary_list(fractional_part)

    if integer_bits[0] == 1:
        exponent_value = len(integer_bits) - 1
        mantissa_source = integer_bits[1:] + fractional_bits
    else:
        try:
            first_one_index = fractional_bits.index(1)
        except ValueError:
            return _build_zero_bits(sign_bit)

        exponent_value = -(first_one_index + 1)
        mantissa_source = fractional_bits[first_one_index + 1:]

    biased_exponent = exponent_value + FLOAT_BIAS

    if biased_exponent >= IEEE_FLOAT_EXP_LIMIT:
        return _build_infinity_bits(sign_bit)

    if biased_exponent <= 0:
        return _build_zero_bits(sign_bit)

    exponent_bits = _pad_left(int_to_binary_list(biased_exponent), FLOAT_EXP_BITS)

    if len(mantissa_source) >= FLOAT_MANTISSA_BITS:
        mantissa_bits = mantissa_source[:FLOAT_MANTISSA_BITS]
    else:
        mantissa_bits = mantissa_source + [0] * (FLOAT_MANTISSA_BITS - len(mantissa_source))

    return [sign_bit] + exponent_bits + mantissa_bits


def from_ieee754(bits: List[int]) -> float:
    sign_bit = bits[0]
    exponent_bits = bits[1:1 + FLOAT_EXP_BITS]
    mantissa_bits = bits[1 + FLOAT_EXP_BITS:]

    exponent_value = binary_list_to_int(exponent_bits)

    if exponent_value == 0 and all(bit == 0 for bit in mantissa_bits):
        return -0.0 if sign_bit == NEGATIVE_SIGN else 0.0

    if exponent_value == IEEE_FLOAT_EXP_LIMIT:
        if all(bit == 0 for bit in mantissa_bits):
            return float("-inf") if sign_bit == NEGATIVE_SIGN else float("inf")
        return float("nan")

    true_exponent = exponent_value - FLOAT_BIAS
    mantissa_value = 1.0 + binary_fraction_to_float(mantissa_bits)
    result = mantissa_value * (2 ** true_exponent)

    return -result if sign_bit == NEGATIVE_SIGN else result