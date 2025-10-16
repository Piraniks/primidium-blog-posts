from dataclasses import dataclass
from decimal import Decimal
from functools import reduce
from operator import add, mul, sub, truediv
from typing import Protocol


@dataclass(frozen=True)
class Explanation:
    label: str | None
    type: str
    value: Decimal
    operands: tuple['Explanation' | Decimal, ...]


class Calculation(Protocol):
    def evaluate(self) -> Decimal:
        raise NotImplementedError()

    def explain(self) -> Explanation:
        raise NotImplementedError()

    @property
    def type_name(self):
        return self.__class__.__name__


class Value(Calculation):
    def __init__(self, value: Decimal, label: str | None):
        self.label = label
        self.value = value

    def evaluate(self) -> Decimal:
        return self.value

    def explain(self) -> Explanation:
        return Explanation(
            label=self.label,
            type=self.type_name,
            value=self.value,
            operands=(self.value,),
        )


class Operation(Calculation):
    def __init__(self, *operands: Calculation, label: str | None):
        self.label = label
        self.operands = operands

    def explain(self) -> Explanation:
        return Explanation(
            label=self.label,
            type=self.type_name,
            value=self.evaluate(),
            operands=tuple(operand.explain() for operand in self.operands),
        )


class Addition(Operation):
    def evaluate(self) -> Decimal:
        return reduce(add, (operand.evaluate() for operand in self.operands))


class Subtraction(Operation):
    def evaluate(self) -> Decimal:
        return reduce(sub, (operand.evaluate() for operand in self.operands))


class Multiplication(Operation):
    def evaluate(self) -> Decimal:
        return reduce(mul, (operand.evaluate() for operand in self.operands))


class Division(Operation):
    def evaluate(self) -> Decimal:
        return reduce(truediv, (operand.evaluate() for operand in self.operands))


class Calculable(Protocol):
    def build_calculations(self) -> Calculation:
        raise NotImplementedError()
