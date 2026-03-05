from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, DivisionByZero
from typing import Union

NumberLike = Union[int, float, str, Decimal]


def to_decimal(value: NumberLike) -> Decimal:
    """
    Convert supported number-like inputs to Decimal.

    Accepts int, float, Decimal, and numeric strings.
    Note: floats are converted via str(float) to reduce binary artifacts.
    """
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, str):
        try:
            return Decimal(value.strip())
        except InvalidOperation as e:
            raise ValueError(f"Invalid numeric string: {value!r}") from e
    raise TypeError(f"Unsupported type: {type(value).__name__}")


def add(a: NumberLike, b: NumberLike) -> Decimal:
    return to_decimal(a) + to_decimal(b)


def sub(a: NumberLike, b: NumberLike) -> Decimal:
    return to_decimal(a) - to_decimal(b)


def mul(a: NumberLike, b: NumberLike) -> Decimal:
    return to_decimal(a) * to_decimal(b)


def div(a: NumberLike, b: NumberLike) -> Decimal:
    da = to_decimal(a)
    db = to_decimal(b)
    try:
        return da / db
    except (DivisionByZero, InvalidOperation) as e:
        # Decimal throws DivisionByZero; also catch invalid divisions defensively.
        raise ZeroDivisionError("Cannot divide by zero") from e


@dataclass
class Core:
    """
    Optional wrapper around arithmetic functions.
    Keeps the API explicit and easy to mock/compose.
    """

    def add(self, a: NumberLike, b: NumberLike) -> Decimal:
        return add(a, b)

    def sub(self, a: NumberLike, b: NumberLike) -> Decimal:
        return sub(a, b)

    def mul(self, a: NumberLike, b: NumberLike) -> Decimal:
        return mul(a, b)

    def div(self, a: NumberLike, b: NumberLike) -> Decimal:
        return div(a, b)