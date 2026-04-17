"""Tokenizer for boolean expressions."""
from __future__ import annotations

from typing import List

from lab2_sem4.constants import (
    SUPPORTED_VARIABLES,
    TOKEN_AND,
    TOKEN_END,
    TOKEN_EQUIV,
    TOKEN_IMPLIES,
    TOKEN_LPAREN,
    TOKEN_NOT,
    TOKEN_OR,
    TOKEN_RPAREN,
    TOKEN_VARIABLE,
)
from lab2_sem4.models import Token


class TokenizerError(ValueError):
    """Raised when tokenizer meets an unsupported character."""


class Tokenizer:
    """Converts a raw expression string to a token list."""

    _SINGLE_CHAR_TOKENS = {
        '!': TOKEN_NOT,
        '¬': TOKEN_NOT,
        '&': TOKEN_AND,
        '∧': TOKEN_AND,
        '|': TOKEN_OR,
        '∨': TOKEN_OR,
        '~': TOKEN_EQUIV,
        '(': TOKEN_LPAREN,
        ')': TOKEN_RPAREN,
    }

    def tokenize(self, expression: str) -> List[Token]:
        normalized = expression.replace(' ', '')
        tokens: List[Token] = []
        position = 0
        while position < len(normalized):
            current_symbol = normalized[position]
            if current_symbol in self._SINGLE_CHAR_TOKENS:
                tokens.append(Token(self._SINGLE_CHAR_TOKENS[current_symbol], current_symbol))
                position += 1
                continue
            if normalized.startswith('->', position) or normalized.startswith('→', position):
                token_value = '->' if normalized.startswith('->', position) else '→'
                tokens.append(Token(TOKEN_IMPLIES, token_value))
                position += len(token_value)
                continue
            if current_symbol in SUPPORTED_VARIABLES:
                tokens.append(Token(TOKEN_VARIABLE, current_symbol))
                position += 1
                continue
            raise TokenizerError(f'Unsupported symbol: {current_symbol}')
        tokens.append(Token(TOKEN_END, ''))
        return tokens
