import enum
from datetime import datetime

from sqlalchemy import String, Text, Enum, DateTime, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class OrderStatus(str, enum.Enum):
    pending = "pending"
    assigned = "assigned"
    in_progress = "in_progress"
    qc = "qc"
    shipped = "shipped"
    awaiting_review = "awaiting_review"
    completed = "completed"
    cancelled = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    status: Mapped[str] = mapped_column(Enum(OrderStatus), default=OrderStatus.pending, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
    custom_size: Mapped[str | None] = mapped_column(String(100), nullable=True)
    custom_color: Mapped[str | None] = mapped_column(String(50), nullable=True)
    custom_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    reference_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_original: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    assignments: Mapped[list["OrderAssignment"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    progress_photos: Mapped[list["OrderProgressPhoto"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class OrderAssignment(Base):
    __tablename__ = "order_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    artisan_id: Mapped[int] = mapped_column(Integer, ForeignKey("artisans.id"), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    order: Mapped["Order"] = relationship(back_populates="assignments")


class OrderProgressPhoto(Base):
    __tablename__ = "order_progress_photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    uploaded_by: Mapped[int] = mapped_column(Integer, nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    order: Mapped["Order"] = relationship(back_populates="progress_photos")


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, unique=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    artisan_id: Mapped[int] = mapped_column(Integer, ForeignKey("artisans.id"), nullable=False)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    order: Mapped["Order"] = relationship()
    product: Mapped["Product"] = relationship()
    artisan: Mapped["Artisan"] = relationship()
    customer: Mapped["User"] = relationship()
