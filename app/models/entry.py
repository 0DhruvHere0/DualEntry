from decimal import Decimal
from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
class Entry(Base):
    __tablename__ = "entries"
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )
    transaction_id: Mapped[int] = mapped_column(
        ForeignKey("transactions.id"),
        nullable=False
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id"),
        nullable=False
    )
    entry_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )
    transaction = relationship(
        "Transaction",
        back_populates="entries"
    )
    account = relationship(
        "Account",
        back_populates="entries"
    )