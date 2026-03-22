from typing import List

def invert_bits(bits: List[int]) -> List[int]:
    return [1 - bit for bit in bits]

def add_binary_lists(a: List[int], b: List[int]) -> List[int]:
    """
    Performs binary addition of two bit lists (a + b).
    Returns a new list. The result length is max(len(a), len(b)) + 1 (potential overflow).
    Handles lists of any length.
    """

    max_len = max(len(a), len(b))

    a_padded = [0] * (max_len - len(a)) + a
    b_padded = [0] * (max_len - len(b)) + b

    result = []
    carry = 0

    for i in range(max_len - 1, -1, -1):
        bit_a = a_padded[i]
        bit_b = b_padded[i]

        current_sum = bit_a + bit_b + carry

        result_bit = current_sum % 2
        carry = 1 if current_sum > 1 else 0

        result.append(result_bit)

    if carry > 0:
        result.append(carry)

    result.reverse()

    return result


