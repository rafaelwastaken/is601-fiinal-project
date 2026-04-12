from sqlalchemy.orm import Session

from app.factories.calculation import CalculationFactory
from app.models.calculation import Calculation
from app.schemas.calculation import CalculationCreate, CalculationUpdate


def create_calculation(db: Session, calculation_in: CalculationCreate) -> Calculation:
    result = CalculationFactory.calculate(
        a=calculation_in.a,
        b=calculation_in.b,
        operation_type=calculation_in.type,
    )

    calculation = Calculation(
        a=calculation_in.a,
        b=calculation_in.b,
        type=calculation_in.type.value,
        result=result,
    )
    db.add(calculation)
    db.commit()
    db.refresh(calculation)
    return calculation


def list_calculations(db: Session) -> list[Calculation]:
    return db.query(Calculation).order_by(Calculation.id.asc()).all()


def get_calculation(db: Session, calculation_id: int) -> Calculation | None:
    return db.query(Calculation).filter(Calculation.id == calculation_id).first()


def update_calculation(db: Session, calculation: Calculation, payload: CalculationUpdate) -> Calculation:
    result = CalculationFactory.calculate(
        a=payload.a,
        b=payload.b,
        operation_type=payload.type,
    )

    calculation.a = payload.a
    calculation.b = payload.b
    calculation.type = payload.type.value
    calculation.result = result

    db.add(calculation)
    db.commit()
    db.refresh(calculation)
    return calculation


def delete_calculation(db: Session, calculation: Calculation) -> None:
    db.delete(calculation)
    db.commit()
