from datetime import datetime

from sqlalchemy import DateTime, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Calculation(Base):
    __tablename__ = "calculations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    a: Mapped[float] = mapped_column(Float, nullable=False)
    b: Mapped[float] = mapped_column(Float, nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    result: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
