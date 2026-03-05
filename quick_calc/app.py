from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from quick_calc.core import Core, to_decimal


def format_decimal(d: Decimal) -> str:
    s = format(d, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s if s else "0"


@dataclass
class CalculatorSession:
    """
    Controller / input-layer independent of UI toolkit.
    Tkinter buttons will call these methods.
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
            return

        current = to_decimal(self._display)

        if self._left is None:
            self._left = current
        else:
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


# ----------------------- Tkinter UI -----------------------

class QuickCalcTk:
    """
    Tkinter UI that delegates all logic to CalculatorSession.
    Provides stable 'button names' for integration tests.
    """

    def __init__(self, root):
        import tkinter as tk

        self.tk = tk
        self.root = root
        self.root.title("Quick-Calc")

        self.session = CalculatorSession()

        self.display_var = tk.StringVar(value=self.session.get_display())

        # Display
        display = tk.Entry(
            root,
            textvariable=self.display_var,
            justify="right",
            font=("Arial", 18),
            state="readonly",
            readonlybackground="white",
        )
        display.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=8, pady=8, ipady=8)

        # Buttons (store references for tests)
        self.buttons = {}

        def add_btn(text, r, c, cmd, colspan=1):
            b = tk.Button(root, text=text, command=cmd, font=("Arial", 14))
            b.grid(row=r, column=c, columnspan=colspan, sticky="nsew", padx=4, pady=4, ipady=6)
            self.buttons[text] = b

        # Row 1
        add_btn("C", 1, 0, self._on_clear)
        add_btn("±", 1, 1, self._on_sign)
        add_btn("/", 1, 2, lambda: self._on_op("/"))
        add_btn("*", 1, 3, lambda: self._on_op("*"))

        # Row 2
        add_btn("7", 2, 0, lambda: self._on_digit("7"))
        add_btn("8", 2, 1, lambda: self._on_digit("8"))
        add_btn("9", 2, 2, lambda: self._on_digit("9"))
        add_btn("-", 2, 3, lambda: self._on_op("-"))

        # Row 3
        add_btn("4", 3, 0, lambda: self._on_digit("4"))
        add_btn("5", 3, 1, lambda: self._on_digit("5"))
        add_btn("6", 3, 2, lambda: self._on_digit("6"))
        add_btn("+", 3, 3, lambda: self._on_op("+"))

        # Row 4
        add_btn("1", 4, 0, lambda: self._on_digit("1"))
        add_btn("2", 4, 1, lambda: self._on_digit("2"))
        add_btn("3", 4, 2, lambda: self._on_digit("3"))
        add_btn("=", 4, 3, self._on_equals)

        # Row 5
        add_btn("0", 5, 0, lambda: self._on_digit("0"), colspan=2)
        add_btn(".", 5, 2, self._on_dot)

        # Layout weights
        root.grid_rowconfigure(0, weight=0)
        for r in range(1, 6):
            root.grid_rowconfigure(r, weight=1)
        for c in range(4):
            root.grid_columnconfigure(c, weight=1)

    def _refresh(self):
        self.display_var.set(self.session.get_display())

    def _on_digit(self, d: str):
        self.session.press_digit(d)
        self._refresh()

    def _on_dot(self):
        self.session.press_dot()
        self._refresh()

    def _on_sign(self):
        self.session.press_sign()
        self._refresh()

    def _on_op(self, op: str):
        self.session.press_op(op)
        self._refresh()

    def _on_equals(self):
        self.session.press_equals()
        self._refresh()

    def _on_clear(self):
        self.session.press_clear()
        self._refresh()


def main() -> None:
    import tkinter as tk

    root = tk.Tk()
    QuickCalcTk(root)
    root.mainloop()


if __name__ == "__main__":
    main()