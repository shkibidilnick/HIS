from typing import List
from src.constants import FLOAT_EXP_BITS, FLOAT_MANTISSA_BITS, FLOAT_BIAS, POSITIVE_SIGN, NEGATIVE_SIGN
from src.utils import int_to_binary_list, fraction_to_binary_list, binary_list_to_int, binary_fraction_to_float, delete_leading_zeros

def to_ieee754(decimal_float: float) -> List[int]:
    if decimal_float == 0.0:
        return [POSITIVE_SIGN] + [0] * FLOAT_EXP_BITS + [0] * FLOAT_MANTISSA_BITS

    sign_bit = NEGATIVE_SIGN if decimal_float < 0 else POSITIVE_SIGN
    value = abs(decimal_float)

    int_part = int(value)
    frac_part = value - int_part

    int_bits = int_to_binary_list(int_part)
    frac_bits = fraction_to_binary_list(frac_part)

    exponent = 0
    mantissa_raw = []

    if int_bits[0] == 1: # Value >= 1.0 (5.0 -> 101)
        exponent = len(int_bits) - 1
        mantissa_raw = int_bits[1:] + frac_bits
    else: # Value < 1.0 (0.5 -> 0.1)
        try:
            first_one_idx = frac_bits.index(1)
            exponent = -(first_one_idx + 1)
            mantissa_raw = frac_bits[first_one_idx + 1:]
        except ValueError:
            return [POSITIVE_SIGN] + [0] * (FLOAT_EXP_BITS + FLOAT_MANTISSA_BITS)

    biased_exp = exponent + FLOAT_BIAS

    if biased_exp >= 2 ** FLOAT_EXP_BITS:
        return [sign_bit] + [1] * FLOAT_EXP_BITS + [0] * FLOAT_MANTISSA_BITS

    if biased_exp <= 0:
        return [sign_bit] + [0] * (FLOAT_EXP_BITS + FLOAT_MANTISSA_BITS)

    exp_bits = int_to_binary_list(biased_exp)
    exp_bits = [0] * (FLOAT_EXP_BITS - len(exp_bits)) + exp_bits

    if len(mantissa_raw) >= FLOAT_MANTISSA_BITS:
        mantissa_bits = mantissa_raw[:FLOAT_MANTISSA_BITS]
    else:
        mantissa_bits = mantissa_raw + [0] * (FLOAT_MANTISSA_BITS - len(mantissa_raw))

    return [sign_bit] + exp_bits + mantissa_bits

def from_ieee754(bits: List[int]) -> float:
    sign_bit = bits[0]
    exp_bits = bits[1:1+FLOAT_EXP_BITS]
    mantissa_bits = bits[1+FLOAT_EXP_BITS:]

    exp_val = binary_list_to_int(exp_bits)

    if exp_val == 0 and all(b == 0 for b in mantissa_bits):
        return -0.0 if sign_bit == NEGATIVE_SIGN else 0.0

    if exp_val == 255:
        if all(b == 0 for b in mantissa_bits):
            return float('-inf') if sign_bit == NEGATIVE_SIGN else float('inf')
        return float('nan')

    true_exp = exp_val - FLOAT_BIAS
    mantissa_val = 1.0 + binary_fraction_to_float(mantissa_bits)
    result = mantissa_val * (2 ** true_exp)

    return -result if sign_bit == NEGATIVE_SIGN else result