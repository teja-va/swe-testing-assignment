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
    core: Core = field(default_factory=Core)
    _display: str = "0"              # what UI shows (expression)
    _current_input: str = "0"        # the number user is typing
    _left: Optional[Decimal] = None
    _op: Optional[str] = None
    _reset_next_input: bool = False
    _error: Optional[str] = None
    _last_left_str: Optional[str] = None   # store left operand as text for pretty expression
    _last_right_str: Optional[str] = None  # store right operand as text for pretty expression

    def get_display(self) -> str:
        return self._error if self._error is not None else self._display

    def _sync_display(self) -> None:
        """Update expression line depending on current state."""
        if self._error is not None:
            self._display = self._error
            return

        if self._op is None or self._left is None:
            # Only typing a single number
            self._display = self._current_input
            return

        # We have left + operator, and maybe right being typed
        left_txt = self._last_left_str if self._last_left_str is not None else format_decimal(self._left)
        right_txt = "" if self._reset_next_input else self._current_input
        self._display = f"{left_txt}{self._op}{right_txt}"

    def press_clear(self) -> None:
        self._display = "0"
        self._current_input = "0"
        self._left = None
        self._op = None
        self._reset_next_input = False
        self._error = None
        self._last_left_str = None
        self._last_right_str = None

    def press_digit(self, ch: str) -> None:
        if self._error is not None:
            self.press_clear()

        if ch not in "0123456789":
            raise ValueError("press_digit expects a single digit 0-9")

        if self._reset_next_input:
            self._current_input = "0"
            self._reset_next_input = False

        if self._current_input == "0":
            self._current_input = ch
        else:
            self._current_input += ch

        self._sync_display()

    def press_dot(self) -> None:
        if self._error is not None:
            self.press_clear()

        if self._reset_next_input:
            self._current_input = "0"
            self._reset_next_input = False

        if "." not in self._current_input:
            self._current_input += "."

        self._sync_display()

    def press_sign(self) -> None:
        if self._error is not None:
            self.press_clear()

        if self._current_input.startswith("-"):
            self._current_input = self._current_input[1:]
        else:
            if self._current_input != "0":
                self._current_input = "-" + self._current_input

        self._sync_display()

    def press_op(self, op: str) -> None:
        if op not in {"+", "-", "*", "/"}:
            raise ValueError("Unsupported operation")

        if self._error is not None:
            return

        current_dec = to_decimal(self._current_input)

        if self._left is None:
            self._left = current_dec
            self._last_left_str = self._current_input
        else:
            # chaining operations: compute intermediate result if user already typed right operand
            if self._op is not None and not self._reset_next_input:
                result = self._apply(self._left, self._op, current_dec)
                if result is None:
                    self._sync_display()
                    return
                self._left = result
                self._last_left_str = format_decimal(result)
                self._current_input = self._last_left_str

        self._op = op
        self._reset_next_input = True
        self._sync_display()

    def press_equals(self) -> None:
        if self._error is not None:
            return
        if self._left is None or self._op is None:
            return

        right_str = self._current_input
        right_dec = to_decimal(right_str)

        result = self._apply(self._left, self._op, right_dec)
        if result is None:
            self._sync_display()
            return

        left_txt = self._last_left_str if self._last_left_str is not None else format_decimal(self._left)
        res_txt = format_decimal(result)

        # Show full action: 5+3=8
        self._display = f"{left_txt}{self._op}{right_str}={res_txt}"

        # Reset state, but keep current_input as result so next operations can continue naturally
        self._current_input = res_txt
        self._left = None
        self._op = None
        self._reset_next_input = True
        self._last_left_str = None
        self._last_right_str = None

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