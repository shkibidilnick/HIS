"""AST nodes for boolean expressions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


class ExpressionNode:
    def evaluate(self, variables: Dict[str, int]) -> int:
        raise NotImplementedError


@dataclass(frozen=True)
class VariableNode(ExpressionNode):
    name: str

    def evaluate(self, variables: Dict[str, int]) -> int:
        return variables[self.name]


@dataclass(frozen=True)
class UnaryOperationNode(ExpressionNode):
    operand: ExpressionNode


@dataclass(frozen=True)
class NotNode(UnaryOperationNode):
    def evaluate(self, variables: Dict[str, int]) -> int:
        return 1 - self.operand.evaluate(variables)


@dataclass(frozen=True)
class BinaryOperationNode(ExpressionNode):
    left: ExpressionNode
    right: ExpressionNode


@dataclass(frozen=True)
class AndNode(BinaryOperationNode):
    def evaluate(self, variables: Dict[str, int]) -> int:
        return self.left.evaluate(variables) & self.right.evaluate(variables)


@dataclass(frozen=True)
class OrNode(BinaryOperationNode):
    def evaluate(self, variables: Dict[str, int]) -> int:
        return self.left.evaluate(variables) | self.right.evaluate(variables)


@dataclass(frozen=True)
class ImpliesNode(BinaryOperationNode):
    def evaluate(self, variables: Dict[str, int]) -> int:
        left_value = self.left.evaluate(variables)
        right_value = self.right.evaluate(variables)
        return (1 - left_value) | right_value


@dataclass(frozen=True)
class EquivalenceNode(BinaryOperationNode):
    def evaluate(self, variables: Dict[str, int]) -> int:
        return 1 if self.left.evaluate(variables) == self.right.evaluate(variables) else 0
