"""High-level expression object."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from lab2_sem4.constants import MAX_VARIABLE_COUNT
from lab2_sem4.core.ast_nodes import ExpressionNode
from lab2_sem4.core.parser import Parser
from lab2_sem4.core.tokenizer import Tokenizer


@dataclass(frozen=True)
class BooleanExpression:
    source: str
    ast: ExpressionNode
    variables: Tuple[str, ...]

    def evaluate(self, assignment: Dict[str, int]) -> int:
        return self.ast.evaluate(assignment)


class BooleanExpressionFactory:
    def __init__(self) -> None:
        self._tokenizer = Tokenizer()
        self._parser = Parser()

    def create(self, source: str) -> BooleanExpression:
        tokens = self._tokenizer.tokenize(source)
        ast = self._parser.parse(tokens)
        variables = tuple(sorted({token.value for token in tokens if token.value.isalpha()}))
        if not variables:
            raise ValueError('Expression must contain at least one variable.')
        if len(variables) > MAX_VARIABLE_COUNT:
            raise ValueError(f'At most {MAX_VARIABLE_COUNT} variables are supported.')
        return BooleanExpression(source=source, ast=ast, variables=variables)
