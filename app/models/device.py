from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Device(Base):
    __tablename__ = "devices"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(index=True)
    status: Mapped[str] = mapped_column(default="offline")
    factory_id: Mapped[str] = mapped_column(index=True)