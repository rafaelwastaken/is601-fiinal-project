import pytest
from pydantic import ValidationError

from app.schemas.calculation import CalculationCreate, CalculationType


def test_calculation_create_accepts_valid_payload():
    payload = CalculationCreate(a=10, b=5, type=CalculationType.DIVIDE)
    assert payload.a == 10
    assert payload.b == 5
    assert payload.type == CalculationType.DIVIDE


def test_calculation_create_rejects_divide_by_zero():
    with pytest.raises(ValidationError):
        CalculationCreate(a=10, b=0, type=CalculationType.DIVIDE)


def test_calculation_create_rejects_invalid_type_string():
    with pytest.raises(ValidationError):
        CalculationCreate(a=10, b=5, type="Modulo")
