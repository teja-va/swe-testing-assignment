import pytest
import tkinter as tk

from decimal import Decimal
from quick_calc.core import add, sub, mul, div, to_decimal
from quick_calc.app import QuickCalcTk


# Unit tests

def test_add(): assert add(10, 3) == Decimal("13")

def test_sub(): assert sub(15, 3) == Decimal("12")

def test_mul(): assert mul(10, 3) == Decimal("30")

def test_div(): assert div(9, 3) == Decimal("3")

def test_div_by_zero():
    with pytest.raises(ZeroDivisionError): div(5, 0)

def test_negative_numbers():
    assert add(-10, 3) == Decimal("-7")
    assert sub(-7, -3) == Decimal("-4")

def test_decimal_numbers_from_strings():
    assert add("0.1", "0.2") == Decimal("0.3")
    assert div("1.5", "0.5") == Decimal("3")

def test_very_large_numbers(): assert add("9999999999999999999999999999", 1) == Decimal("10000000000000000000000000000")

def test_to_decimal_rejects_bad_string():
    with pytest.raises(ValueError):
        to_decimal("not-a-number")

# Integration tests

def _get_result_text(display: str) -> str:
    # Supports "8" OR "5+3=8"
    if "=" in display:
        return display.split("=", 1)[1]
    return display


def _assert_display_result(display: str, expected: str) -> None:
    assert _get_result_text(display) == expected


def _new_app():
    root = tk.Tk()
    root.withdraw()
    app = QuickCalcTk(root)
    return root, app

def test_addition_5_plus_3_equals_8():
    root, app = _new_app()
    try:
        app.buttons["5"].invoke()
        app.buttons["+"].invoke()
        app.buttons["3"].invoke()
        app.buttons["="].invoke()
        _assert_display_result(app.display_var.get(), "8")
    finally:
        root.destroy()


def test_addition_10_plus_3_equals_13():
    root, app = _new_app()
    try:
        app.buttons["1"].invoke()
        app.buttons["0"].invoke()
        app.buttons["+"].invoke()
        app.buttons["3"].invoke()
        app.buttons["="].invoke()
        _assert_display_result(app.display_var.get(), "13")
    finally:
        root.destroy()


def test_ui_clear():
    root, app = _new_app()
    try:
        app.buttons["9"].invoke()
        app.buttons["*"].invoke()
        app.buttons["9"].invoke()
        app.buttons["="].invoke()
        _assert_display_result(app.display_var.get(), "81")

        app.buttons["C"].invoke()
        assert app.display_var.get() == "0"
    finally:
        root.destroy()


def test_ui_division_by_zero_shows_error():
    root, app = _new_app()
    try:
        app.buttons["1"].invoke()
        app.buttons["0"].invoke()
        app.buttons["/"].invoke()
        app.buttons["0"].invoke()
        app.buttons["="].invoke()
        assert "Error" in app.display_var.get()
    finally:
        root.destroy()


def test_ui_decimal_input_1_point_5_times_2_equals_3():
    root, app = _new_app()
    try:
        app.buttons["1"].invoke()
        app.buttons["."].invoke()
        app.buttons["5"].invoke()
        app.buttons["*"].invoke()
        app.buttons["2"].invoke()
        app.buttons["="].invoke()
        _assert_display_result(app.display_var.get(), "3")
    finally:
        root.destroy()