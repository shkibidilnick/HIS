from typing import List, Tuple

def int_to_binary_list(value: int) -> List[int]:
    """
    Converts a non-negative integer to a list of bits (MSB first).
    Returns [0] for value 0.
    """
    if value == 0:
        return [0]

    bits = []
    while value > 0:
        bits.append(value % 2)
        value //= 2

    bits.reverse()
    return bits

def binary_list_to_int(bits: List[int]) -> int:
    """
    Converts a list of bits to an integer.
    """
    result = 0
    for bit in bits:
        result = result * 2 + bit
    return result

def fraction_to_binary_list(value: float, limit: int = 60) -> List[int]:
    """
    Converts fractional part (0.0 < value < 1.0) to bits.
    """
    bits = []
    current = value
    for _ in range(limit):
        if current == 0.0:
            break
        current *= 2
        if current >= 1.0:
            bits.append(1)
            current -= 1.0
        else:
            bits.append(0)
    return bits

def binary_fraction_to_float(bits: List[int]) -> float:
    """
    Converts a list of fractional bits to a float value.
    """
    result = 0.0
    for i, bit in enumerate(bits):
        if bit == 1:
            result += 2 ** (-(i + 1))
    return result

def invert_bits(bits: List[int]) -> List[int]:
    return [1 - bit for bit in bits]

def negate_bits(bits: List[int]) -> List[int]:
    inverted = invert_bits(bits)
    negated_value = add_binary_lists(inverted, [1])

    if len(negated_value) > len(bits):
        return negated_value[-len(bits):]

    return negated_value

def pad_lists_to_equal_length(a: List[int], b: List[int]) -> Tuple[List[int], List[int], int]:
    """ Pads the shorter list with zeros on hte left to match lengths."""
    diff = len(a) - len(b)
    if diff > 0:
        max_len = len(a)
        return a, [0] * diff + b, max_len
    elif diff < 0:
        max_len = len(b)
        return [0] * (-diff) + a, b, max_len
    return a, b, len(a)

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
    a_padded, b_padded, max_len = pad_lists_to_equal_length(a, b)

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


def compare_binary_lists(a: List[int], b: List[int]) -> int:
    """
    Compares two binary lists (magnitudes).
    Returns: 1 if a > b, 0 if a == b, -1 if a < b.
    """

    a_clean = delete_leading_zeros(a)
    b_clean = delete_leading_zeros(b)

    if len(a_clean) > len(b_clean):
        return 1
    if len(a_clean) < len(b_clean):
        return -1

    for i in range(len(a_clean)):
        bit_a = a_clean[i]
        bit_b = b_clean[i]

        if bit_a > bit_b:
            return 1
        if bit_a < bit_b:
            return -1

    return 0

def subtract_binary_lists(a: List[int], b: List[int]) -> List[int]:

    a_padded, b_padded, max_len = pad_lists_to_equal_length(a, b)
    neg_b = negate_bits(b_padded)
    result = add_binary_lists(a_padded, neg_b)

    if len(result) > max_len:
        result = result[-max_len:]

    return delete_leading_zeros(result)



