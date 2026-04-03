import os
import sys
from typing import List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from integer.converter import (
    to_direct_code,
    to_reverse_code,
    to_complementary_code,
)
from integer.operations import (
    add_complementary_numbers,
    subtract_complementary_bits,
    multiply_direct_numbers,
    divide_direct_numbers,
)
from floating_point.converter import to_ieee754
from floating_point.operations import (
    add_floats,
    sub_floats,
    mul_floats,
    div_floats,
)
from bcd.converter import decimal_to_5421_bcd
from bcd.operations import add_5421_bcd_numbers
from constants import FLOAT_EXP_BITS


MENU_TEXT = """
================ Binary Representation Lab =================
1. Integer number codes
2. Integer addition in complementary code
3. Integer subtraction in complementary code
4. Integer multiplication in direct code
5. Integer division in direct code
6. Floating-point operations IEEE-754 (32 bit)
7. BCD 5421 addition
0. Exit
"""


FLOAT_MENU_TEXT = """
---------------- Floating-point IEEE-754 ----------------
1. Convert decimal float to IEEE-754
2. Add two floating-point numbers
3. Subtract two floating-point numbers
4. Multiply two floating-point numbers
5. Divide two floating-point numbers
0. Back
---------------------------------------------------------
"""


def bits_to_string(bits: List[int]) -> str:
    return "".join(str(bit) for bit in bits)


def tetrads_to_string(tetrads: List[List[int]]) -> str:
    return " ".join(bits_to_string(tetrad) for tetrad in tetrads)


def format_ieee754(bits: List[int]) -> str:
    sign_bit = bits[0]
    exponent_bits = bits[1:1 + FLOAT_EXP_BITS]
    mantissa_bits = bits[1 + FLOAT_EXP_BITS:]

    return (
        f"{sign_bit} "
        f"{bits_to_string(exponent_bits)} "
        f"{bits_to_string(mantissa_bits)}"
    )


def read_int(prompt_text: str) -> int:
    while True:
        try:
            return int(input(prompt_text))
        except ValueError:
            print("Invalid integer. Please try again.")


def read_float(prompt_text: str) -> float:
    while True:
        try:
            return float(input(prompt_text))
        except ValueError:
            print("Invalid floating-point number. Please try again.")


def print_integer_codes() -> None:
    decimal_value = read_int("Enter integer value: ")

    direct_bits = to_direct_code(decimal_value)
    reverse_bits = to_reverse_code(decimal_value)
    complementary_bits = to_complementary_code(decimal_value)

    print("\nResult:")
    print(f"Decimal:            {decimal_value}")
    print(f"Direct code:        {bits_to_string(direct_bits)}")
    print(f"Reverse code:       {bits_to_string(reverse_bits)}")
    print(f"Complementary code: {bits_to_string(complementary_bits)}")
    print()


def print_integer_addition() -> None:
    first_value = read_int("Enter first integer: ")
    second_value = read_int("Enter second integer: ")

    result_bits, result_value, overflow = add_complementary_numbers(
        first_value,
        second_value,
    )

    print("\nResult:")
    print(f"First decimal:      {first_value}")
    print(f"Second decimal:     {second_value}")
    print(f"Result bits:        {bits_to_string(result_bits)}")
    print(f"Result decimal:     {result_value}")
    print(f"Overflow:           {overflow}")
    print()


def print_integer_subtraction() -> None:
    minuend = read_int("Enter minuend: ")
    subtrahend = read_int("Enter subtrahend: ")

    minuend_bits = to_complementary_code(minuend)
    subtrahend_bits = to_complementary_code(subtrahend)

    result_bits, result_value, overflow = subtract_complementary_bits(
        minuend_bits,
        subtrahend_bits,
    )

    print("\nResult:")
    print(f"Minuend decimal:    {minuend}")
    print(f"Subtrahend decimal: {subtrahend}")
    print(f"Result bits:        {bits_to_string(result_bits)}")
    print(f"Result decimal:     {result_value}")
    print(f"Overflow:           {overflow}")
    print()


def print_integer_multiplication() -> None:
    first_value = read_int("Enter first integer: ")
    second_value = read_int("Enter second integer: ")

    result_bits, result_value, overflow = multiply_direct_numbers(
        first_value,
        second_value,
    )

    print("\nResult:")
    print(f"First decimal:      {first_value}")
    print(f"Second decimal:     {second_value}")
    print(f"Result bits:        {bits_to_string(result_bits)}")
    print(f"Result decimal:     {result_value}")
    print(f"Overflow:           {overflow}")
    print()


def print_integer_division() -> None:
    dividend = read_int("Enter dividend: ")
    divisor = read_int("Enter divisor: ")

    try:
        integer_bits, fractional_bits, sign_bit, result_value = divide_direct_numbers(
            dividend,
            divisor,
        )
    except ZeroDivisionError as error:
        print(f"\nError: {error}\n")
        return

    print("\nResult:")
    print(f"Dividend decimal:   {dividend}")
    print(f"Divisor decimal:    {divisor}")
    print(f"Integer bits:       {bits_to_string(integer_bits)}")
    print(f"Fractional bits:    {bits_to_string(fractional_bits)}")
    print(f"Sign bit:           {sign_bit}")
    print(f"Result decimal:     {result_value:.5f}")
    print()


def print_float_conversion() -> None:
    decimal_value = read_float("Enter floating-point number: ")
    ieee_bits = to_ieee754(decimal_value)

    print("\nResult:")
    print(f"Decimal:            {decimal_value}")
    print(f"IEEE-754 bits:      {format_ieee754(ieee_bits)}")
    print()


def print_float_addition() -> None:
    first_value = read_float("Enter first floating-point number: ")
    second_value = read_float("Enter second floating-point number: ")

    result_bits, result_value = add_floats(first_value, second_value)

    print("\nResult:")
    print(f"First decimal:      {first_value}")
    print(f"Second decimal:     {second_value}")
    print(f"Result bits:        {format_ieee754(result_bits)}")
    print(f"Result decimal:     {result_value}")
    print()


def print_float_subtraction() -> None:
    first_value = read_float("Enter first floating-point number: ")
    second_value = read_float("Enter second floating-point number: ")

    result_bits, result_value = sub_floats(first_value, second_value)

    print("\nResult:")
    print(f"First decimal:      {first_value}")
    print(f"Second decimal:     {second_value}")
    print(f"Result bits:        {format_ieee754(result_bits)}")
    print(f"Result decimal:     {result_value}")
    print()


def print_float_multiplication() -> None:
    first_value = read_float("Enter first floating-point number: ")
    second_value = read_float("Enter second floating-point number: ")

    result_bits, result_value = mul_floats(first_value, second_value)

    print("\nResult:")
    print(f"First decimal:      {first_value}")
    print(f"Second decimal:     {second_value}")
    print(f"Result bits:        {format_ieee754(result_bits)}")
    print(f"Result decimal:     {result_value}")
    print()


def print_float_division() -> None:
    dividend = read_float("Enter dividend: ")
    divisor = read_float("Enter divisor: ")

    result_bits, result_value = div_floats(dividend, divisor)

    print("\nResult:")
    print(f"Dividend decimal:   {dividend}")
    print(f"Divisor decimal:    {divisor}")
    print(f"Result bits:        {format_ieee754(result_bits)}")
    print(f"Result decimal:     {result_value}")
    print()


def handle_floating_point_menu() -> None:
    while True:
        print(FLOAT_MENU_TEXT)
        choice = input("Choose action: ").strip()

        if choice == "1":
            print_float_conversion()
        elif choice == "2":
            print_float_addition()
        elif choice == "3":
            print_float_subtraction()
        elif choice == "4":
            print_float_multiplication()
        elif choice == "5":
            print_float_division()
        elif choice == "0":
            return
        else:
            print("Unknown menu item. Please try again.\n")


def print_bcd_addition() -> None:
    first_value = read_int("Enter first non-negative integer: ")
    second_value = read_int("Enter second non-negative integer: ")

    try:
        first_bcd = decimal_to_5421_bcd(first_value)
        second_bcd = decimal_to_5421_bcd(second_value)
        result_bcd, result_decimal = add_5421_bcd_numbers(first_value, second_value)
    except ValueError as error:
        print(f"\nError: {error}\n")
        return

    print("\nResult:")
    print(f"First decimal:      {first_value}")
    print(f"First 5421 BCD:     {tetrads_to_string(first_bcd)}")
    print(f"Second decimal:     {second_value}")
    print(f"Second 5421 BCD:    {tetrads_to_string(second_bcd)}")
    print(f"Result 5421 BCD:    {tetrads_to_string(result_bcd)}")
    print(f"Result decimal:     {result_decimal}")
    print()


def main() -> None:
    while True:
        print(MENU_TEXT)
        choice = input("Choose action: ").strip()

        try:
            if choice == "1":
                print_integer_codes()
            elif choice == "2":
                print_integer_addition()
            elif choice == "3":
                print_integer_subtraction()
            elif choice == "4":
                print_integer_multiplication()
            elif choice == "5":
                print_integer_division()
            elif choice == "6":
                handle_floating_point_menu()
            elif choice == "7":
                print_bcd_addition()
            elif choice == "0":
                print("Program finished.")
                break
            else:
                print("Unknown menu item. Please try again.\n")
        except ValueError as error:
            print(f"\nError: {error}\n")


if __name__ == "__main__":
    main()
