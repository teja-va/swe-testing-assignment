from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from quick_calc.core import Core, to_decimal


def format_decimal(d: Decimal) -> str:
    """
    Format Decimal for display:
    - remove trailing zeros
    - avoid scientific notation for typical calculator usage
    """
    # Normalize can produce exponent; quantize is overkill.
    s = format(d, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s if s else "0"


@dataclass
class CalculatorSession:
    """
    A simple "button-driven" calculator session.
    Supports: digits, '.', unary '-' via typing '-'
    Operations: +, -, *, /
    Buttons: '=', 'C'
    """
    core: Core = field(default_factory=Core)
    _display: str = "0"
    _left: Optional[Decimal] = None
    _op: Optional[str] = None
    _reset_next_input: bool = False
    _error: Optional[str] = None

    def get_display(self) -> str:
        return self._error if self._error is not None else self._display

    def press_clear(self) -> None:
        self._display = "0"
        self._left = None
        self._op = None
        self._reset_next_input = False
        self._error = None

    def press_digit(self, ch: str) -> None:
        if self._error is not None:
            # If in error state, start fresh on input
            self.press_clear()

        if ch not in "0123456789":
            raise ValueError("press_digit expects a single digit 0-9")

        if self._reset_next_input:
            self._display = "0"
            self._reset_next_input = False

        if self._display == "0":
            self._display = ch
        else:
            self._display += ch

    def press_dot(self) -> None:
        if self._error is not None:
            self.press_clear()

        if self._reset_next_input:
            self._display = "0"
            self._reset_next_input = False

        if "." not in self._display:
            self._display += "."

    def press_sign(self) -> None:
        """
        Toggle sign of current display value.
        """
        if self._error is not None:
            self.press_clear()

        if self._display.startswith("-"):
            self._display = self._display[1:]
        else:
            if self._display != "0":
                self._display = "-" + self._display

    def press_op(self, op: str) -> None:
        if op not in {"+", "-", "*", "/"}:
            raise ValueError("Unsupported operation")

        if self._error is not None:
            # Can't proceed while error is shown; keep error until cleared or new input.
            return

        current = to_decimal(self._display)

        if self._left is None:
            self._left = current
        else:
            # If chaining operations, compute intermediate result first
            if self._op is not None and not self._reset_next_input:
                result = self._apply(self._left, self._op, current)
                if result is None:
                    return
                self._left = result
                self._display = format_decimal(result)

        self._op = op
        self._reset_next_input = True

    def press_equals(self) -> None:
        if self._error is not None:
            return
        if self._left is None or self._op is None:
            return

        right = to_decimal(self._display)
        result = self._apply(self._left, self._op, right)
        if result is None:
            return

        self._display = format_decimal(result)
        self._left = None
        self._op = None
        self._reset_next_input = True

    def _apply(self, a: Decimal, op: str, b: Decimal) -> Optional[Decimal]:
        try:
            if op == "+":
                return self.core.add(a, b)
            if op == "-":
                return self.core.sub(a, b)
            if op == "*":
                return self.core.mul(a, b)
            if op == "/":
                return self.core.div(a, b)
        except ZeroDivisionError:
            self._error = "Error: Division by zero"
            return None
        return None


def main() -> None:
    """
    Minimal CLI runner (not required for tests, but useful to demonstrate 'run app').
    Example:
      digits: 5  +  3  =
      C clears
      q quits
    """
    s = CalculatorSession()
    print("Quick-Calc (CLI). Type digits, '.', '+-*/', '=', 'C' to clear, 'q' to quit.")
    print("Display:", s.get_display())

    while True:
        token = input("> ").strip()
        if token.lower() in {"q", "quit", "exit"}:
            break
        if token == "C":
            s.press_clear()
        elif token == "=":
            s.press_equals()
        elif token == ".":
            s.press_dot()
        elif token in {"+", "-", "*", "/"}:
            s.press_op(token)
        elif token == "±":
            s.press_sign()
        elif token.isdigit():
            for ch in token:
                s.press_digit(ch)
        else:
            print("Unknown input. Use digits, '.', '+-*/', '=', 'C', 'q'.")
        print("Display:", s.get_display())


if __name__ == "__main__":
    main()