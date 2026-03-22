from typing import List, Tuple
from src.constants import BIT_SIZE
from src.utils import add_binary_lists
from src.integer.converter import to_complementary_code, from_complementary_code

def add_complementary_numbers(a_decimal: int, b_decimal: int) -> Tuple[List[int], int, bool]:
    """
    Adds two integers using Complementary Code
    :param a_decimal: First integer
    :param b_decimal: Second integer
    :return: A tuple with
    - result_bits (list of 32 bits)
    - result_decimal(the integer interpretation of the result)
    """
    a_bits = to_complementary_code(a_decimal)
    b_bits = to_complementary_code(b_decimal)

    raw_result = add_binary_lists(a_bits, b_bits)

    if len(raw_result) > BIT_SIZE:
        result_bits = raw_result[-BIT_SIZE:]
    else:
        result_bits = raw_result

    sign_a = a_bits[0]
    sign_b = b_bits[0]
    sign_res = result_bits[0]

    is_overflow = False

    if sign_a == sign_b and sign_res != sign_a:
        is_overflow = True

    result_decimal = from_complementary_code(result_bits)

    return result_bits, result_decimal, is_overflow
