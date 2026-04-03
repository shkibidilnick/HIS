from typing import List

BCD_DIGIT_BITS = 4

BCD_5421_DIGIT_MAP = {
    0: [0, 0, 0, 0],
    1: [0, 0, 0, 1],
    2: [0, 0, 1, 0],
    3: [0, 0, 1, 1],
    4: [0, 1, 0, 0],
    5: [1, 0, 0, 0],
    6: [1, 0, 0, 1],
    7: [1, 0, 1, 0],
    8: [1, 0, 1, 1],
    9: [1, 1, 0, 0],
}


def digit_to_5421_bcd(digit: int) -> List[int]:
    if digit not in BCD_5421_DIGIT_MAP:
        raise ValueError(f"Digit {digit} is out of range for 5421 BCD")

    return BCD_5421_DIGIT_MAP[digit][:]


def bcd_5421_to_digit(bits: List[int]) -> int:
    if len(bits) != BCD_DIGIT_BITS:
        raise ValueError("BCD tetrad must contain exactly 4 bits")

    for digit, digit_bits in BCD_5421_DIGIT_MAP.items():
        if digit_bits == bits:
            return digit

    raise ValueError(f"Bits {bits} are not a valid 5421 BCD tetrad")


def decimal_to_5421_bcd(value: int) -> List[List[int]]:
    if value < 0:
        raise ValueError("5421 BCD converter supports only non-negative integers")

    decimal_digits = str(value)
    return [digit_to_5421_bcd(int(digit)) for digit in decimal_digits]


def bcd_5421_to_decimal(tetrads: List[List[int]]) -> int:
    if not tetrads:
        raise ValueError("BCD number must contain at least one tetrad")

    digits = [str(bcd_5421_to_digit(tetrad)) for tetrad in tetrads]
    return int("".join(digits))