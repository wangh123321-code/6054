from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Artisan(Base):
    __tablename__ = "artisans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    specialty: Mapped[str | None] = mapped_column(String(200), nullable=True)
    monthly_capacity: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    schedules: Mapped[list["ArtisanSchedule"]] = relationship(back_populates="artisan", cascade="all, delete-orphan")


class ArtisanSchedule(Base):
    __tablename__ = "artisan_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    artisan_id: Mapped[int] = mapped_column(Integer, ForeignKey("artisans.id", ondelete="CASCADE"), nullable=False)
    year_month: Mapped[int] = mapped_column(Integer, nullable=False)
    assigned_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    artisan: Mapped["Artisan"] = relationship(back_populates="schedules")
