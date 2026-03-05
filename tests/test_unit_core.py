import pytest

from decimal import Decimal
from quick_calc.core import add, sub, mul, div, to_decimal


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