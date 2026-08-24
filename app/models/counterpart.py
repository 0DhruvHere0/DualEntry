from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
class Counterpart(Base):
    __tablename__ = "counterparts"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "counterpart_id",
            name="uq_user_counterpart"
        ),
    )
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )
    counterpart_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )
    relationship_type: Mapped[str] = mapped_column(
        String(50),
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
        back_populates="counterparts"
    )
    counterpart = relationship(
        "User",
        foreign_keys=[counterpart_id],
        back_populates="counterpart_of"
    )