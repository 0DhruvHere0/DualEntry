from datetime import datetime
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base
class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
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