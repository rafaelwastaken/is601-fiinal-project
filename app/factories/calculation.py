from app.schemas.calculation import CalculationType


class CalculationFactory:
    @staticmethod
    def calculate(a: float, b: float, operation_type: CalculationType) -> float:
        operations = {
            CalculationType.ADD: lambda x, y: x + y,
            CalculationType.SUB: lambda x, y: x - y,
            CalculationType.MULTIPLY: lambda x, y: x * y,
            CalculationType.DIVIDE: lambda x, y: x / y,
        }

        operation = operations.get(operation_type)
        if operation is None:
            raise ValueError("unsupported calculation type")

        return operation(a, b)
