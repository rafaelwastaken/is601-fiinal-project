from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CalculationType(str, Enum):
    ADD = "Add"
    SUB = "Sub"
    MULTIPLY = "Multiply"
    DIVIDE = "Divide"


class CalculationCreate(BaseModel):
    a: float = Field(description="Left operand")
    b: float = Field(description="Right operand")
    type: CalculationType

    @model_validator(mode="after")
    def validate_division(self) -> "CalculationCreate":
        if self.type == CalculationType.DIVIDE and self.b == 0:
            raise ValueError("division by zero is not allowed")
        return self


class CalculationUpdate(CalculationCreate):
    pass


class CalculationRead(BaseModel):
    id: int
    a: float
    b: float
    type: CalculationType
    result: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
