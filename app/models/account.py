from datetime import datetime
from sqlalchemy import DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint
class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "name",
            name= "uq_user_account_name"
        ),
    )
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    user = relationship("User", back_populates="accounts")