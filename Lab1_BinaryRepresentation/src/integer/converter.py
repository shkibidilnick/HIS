from typing import List

from src.constants import BIT_SIZE, POSITIVE_SIGN, NEGATIVE_SIGN, MAX_VALUE, MIN_VALUE
from utils import int_to_binary_list, invert_bits, add_binary_lists, binary_list_to_int


def _get_module_bits(decimal_value: int) -> List[int]:
    """
    Helper function for getting module number in binary view.
    Give number -> get list filled with 0 and 1.
    """

    bits = int_to_binary_list(abs(decimal_value))
    padding_size = (BIT_SIZE - 1) - len(bits)

    if padding_size > 0:
        bits = [0] * padding_size + bits

    return bits

def to_direct_code(decimal_value: int) -> List[int]:
    """
    Function for int -> direct code.
    Format: [Sign, Module]
    """
    if abs(decimal_value) > MAX_VALUE:
        raise ValueError(f"The number {decimal_value} too large for {BIT_SIZE} bits")

    if decimal_value < 0:
        sign_bit = NEGATIVE_SIGN
    else:
        sign_bit = POSITIVE_SIGN

    module_bits = _get_module_bits(decimal_value)
    full_binary_code = [sign_bit] + module_bits

    return full_binary_code

def from_direct_code(bits: List[int]) -> int:

    sign_bit = bits[0]
    module_bits = bits[1:]

    value = binary_list_to_int(module_bits)
    if sign_bit == NEGATIVE_SIGN:
        return -value

    return value

def to_reverse_code(decimal_value: int) -> List[int]:
    """
    Converts an integer to Reverse Code representation.
    Pos. numb: same as Direct Code.
    Neg numb: invert all bits of the absolute value
    """
    direct_bits = to_direct_code(decimal_value)

    if decimal_value >= 0:
        return direct_bits
    else:
        result = direct_bits[:]
        result[1:] = invert_bits(result[1:])
        return result

def to_complementary_code(decimal_value: int) -> List[int]:
    """"
    Converts an integer to Complementary Code.
    Positive numbers: same as Direct Code.
    Negative numbers: Reverse Code + 1
    Handles the specific case of MIN_VALUE which exists in Comp Code but not in Direct.
    """
    if decimal_value == MIN_VALUE:
        return [NEGATIVE_SIGN] + [0] * (BIT_SIZE - 1)

    if decimal_value >= 0:
        return to_direct_code(decimal_value)

    reverse_bits = to_reverse_code(decimal_value)
    return add_binary_lists(reverse_bits, [1])

def from_complementary_code(bits: List[int]) -> int:
    if bits[0] == POSITIVE_SIGN:
        return binary_list_to_int(bits[1:])

    inverted_value = invert_bits(bits[1:])
    result_bits = add_binary_lists(inverted_value, [1])
    decimal_value = binary_list_to_int(result_bits)
    return -decimal_value



        


