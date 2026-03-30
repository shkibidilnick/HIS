from typing import List

def invert_bits(bits: List[int]) -> List[int]:
    return [1 - bit for bit in bits]

def negate_bits(bits: List[int]) -> List[int]:
    inverted = invert_bits(bits)
    negated_value = add_binary_lists(inverted, [1])

    if len(negated_value) > len(bits):
        return negated_value[-len(bits):]

    return negated_value

def delete_leading_zeros(bits: List[int]) -> List[int]:
    for i, bit in enumerate(bits):
        if bit == 1:
            return bits[i:]
    # return [0] if all zeros.
    return [0]

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

def multiply_binary_lists(a: List[int], b: List[int]) -> List[int]:
    """
    Multiplies two lists of bits (magnitudes) using the shift-and-add algorithm.
    Works with MSB-first format (e.g., [0, 0, 1, 0] is 2).
    """
    if all(bit == 0 for bit in a) or all(bit == 0 for bit in b):
        return [0]

    result = [0]
    for i in range(len(b)):
        bit = b[i]

        if bit == 1:
            shift = len(b) - 1 - i
            shifted_a = a + [0] * shift

            result = add_binary_lists(result, shifted_a)

    return result

