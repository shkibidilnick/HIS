from typing import List
from src.constants import BIT_SIZE, POSITIVE_SIGN, NEGATIVE_SIGN, MAX_VALUE

def _get_module_bits(decimal_value: int) -> List[int]:
    """
    Helper function for getting module number in binary view.
    Give number -> get list filled with 0 and 1.
    """
    module = abs(decimal_value)
    if module == 0:
        return [0] * (BIT_SIZE - 1)

    bits = []
    while module > 0:
        remainder = module % 2
        bits.append(remainder)
        module = module // 2
    bits.reverse()

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