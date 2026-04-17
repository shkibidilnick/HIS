# Lab2_Sem4

Boolean function analyzer for AOIS laboratory work 2.

## Features

- expression parsing without `eval`
- truth table generation
- SDNF and SKNF generation
- numeric and index forms
- Post class analysis
- Zhegalkin polynomial
- fictive variable detection
- boolean derivatives of orders 1..4
- exact minimization for DNF and CNF
- Karnaugh map output for 1..4 variables

## Run

```bash
python -m lab2_sem4.cli.main
```

## Tests

```bash
python -m unittest discover -s tests -v
coverage run -m unittest discover -s tests
coverage report -m
```
