from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )
    counterpart_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )
    description: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    user = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="transactions"
    )
    counterpart = relationship(
        "User",
        foreign_keys=[counterpart_id],
        back_populates="counterpart_transactions"
    )
    entries= relationship(
        "Entry",
        back_populates="transaction"
    )