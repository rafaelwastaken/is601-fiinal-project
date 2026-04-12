import pytest

from app.factories.calculation import CalculationFactory
from app.schemas.calculation import CalculationType


@pytest.mark.parametrize(
    ("a", "b", "operation", "expected"),
    [
        (8, 2, CalculationType.ADD, 10),
        (8, 2, CalculationType.SUB, 6),
        (8, 2, CalculationType.MULTIPLY, 16),
        (8, 2, CalculationType.DIVIDE, 4),
    ],
)
def test_calculation_factory_operations(a, b, operation, expected):
    result = CalculationFactory.calculate(a, b, operation)
    assert result == expected


def test_calculation_factory_rejects_unknown_type():
    with pytest.raises(ValueError):
        CalculationFactory.calculate(1, 2, "Modulo")
