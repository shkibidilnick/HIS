"""Recursive descent parser for boolean expressions."""
from __future__ import annotations

from typing import List

from lab2_sem4.constants import (
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
from lab2_sem4.core.ast_nodes import (
    AndNode,
    EquivalenceNode,
    ExpressionNode,
    ImpliesNode,
    NotNode,
    OrNode,
    VariableNode,
)
from lab2_sem4.models import Token


class ParserError(ValueError):
    """Raised when the token sequence is syntactically incorrect."""


class Parser:
    def parse(self, tokens: List[Token]) -> ExpressionNode:
        self._tokens = tokens
        self._position = 0
        expression = self._parse_equivalence()
        self._expect(TOKEN_END)
        return expression

    def _current(self) -> Token:
        return self._tokens[self._position]

    def _advance(self) -> Token:
        token = self._current()
        self._position += 1
        return token

    def _expect(self, token_type: str) -> Token:
        current = self._current()
        if current.token_type != token_type:
            raise ParserError(f'Expected {token_type}, got {current.token_type}')
        return self._advance()

    def _parse_equivalence(self) -> ExpressionNode:
        node = self._parse_implication()
        while self._current().token_type == TOKEN_EQUIV:
            self._advance()
            node = EquivalenceNode(node, self._parse_implication())
        return node

    def _parse_implication(self) -> ExpressionNode:
        node = self._parse_or()
        while self._current().token_type == TOKEN_IMPLIES:
            self._advance()
            node = ImpliesNode(node, self._parse_or())
        return node

    def _parse_or(self) -> ExpressionNode:
        node = self._parse_and()
        while self._current().token_type == TOKEN_OR:
            self._advance()
            node = OrNode(node, self._parse_and())
        return node

    def _parse_and(self) -> ExpressionNode:
        node = self._parse_unary()
        while self._current().token_type == TOKEN_AND:
            self._advance()
            node = AndNode(node, self._parse_unary())
        return node

    def _parse_unary(self) -> ExpressionNode:
        current = self._current()
        if current.token_type == TOKEN_NOT:
            self._advance()
            return NotNode(self._parse_unary())
        if current.token_type == TOKEN_VARIABLE:
            return VariableNode(self._advance().value)
        if current.token_type == TOKEN_LPAREN:
            self._advance()
            node = self._parse_equivalence()
            self._expect(TOKEN_RPAREN)
            return node
        raise ParserError(f'Unexpected token: {current.token_type}')
