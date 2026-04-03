from typing import List, Tuple

from bcd.converter import (
    digit_to_5421_bcd,
    bcd_5421_to_digit,
    decimal_to_5421_bcd,
    bcd_5421_to_decimal,
)


def _add_decimal_digits(
    first_digit: int,
    second_digit: int,
    carry_in: int,
) -> Tuple[int, int]:
    digit_sum = first_digit + second_digit + carry_in

    if digit_sum >= 10:
        return digit_sum - 10, 1

    return digit_sum, 0


def _add_5421_tetrads(
    first_tetrad: List[int],
    second_tetrad: List[int],
    carry_in: int,
) -> Tuple[List[int], int]:
    first_digit = bcd_5421_to_digit(first_tetrad)
    second_digit = bcd_5421_to_digit(second_tetrad)

    result_digit, carry_out = _add_decimal_digits(
        first_digit,
        second_digit,
        carry_in,
    )

    result_tetrad = digit_to_5421_bcd(result_digit)
    return result_tetrad, carry_out


def add_5421_bcd_numbers(
    first_decimal: int,
    second_decimal: int,
) -> Tuple[List[List[int]], int]:
    if first_decimal < 0 or second_decimal < 0:
        raise ValueError("5421 BCD addition supports only non-negative integers")

    first_tetrads = decimal_to_5421_bcd(first_decimal)
    second_tetrads = decimal_to_5421_bcd(second_decimal)

    max_length = max(len(first_tetrads), len(second_tetrads))
    zero_tetrad = digit_to_5421_bcd(0)

    padded_first = [zero_tetrad[:] for _ in range(max_length - len(first_tetrads))] + first_tetrads
    padded_second = [zero_tetrad[:] for _ in range(max_length - len(second_tetrads))] + second_tetrads

    result_tetrads_reversed = []
    carry = 0

    for index in range(max_length - 1, -1, -1):
        result_tetrad, carry = _add_5421_tetrads(
            padded_first[index],
            padded_second[index],
            carry,
        )
        result_tetrads_reversed.append(result_tetrad)

    if carry == 1:
        result_tetrads_reversed.append(digit_to_5421_bcd(carry))

    result_tetrads = list(reversed(result_tetrads_reversed))
    result_decimal = bcd_5421_to_decimal(result_tetrads)

    return result_tetrads, result_decimal