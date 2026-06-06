from datetime import datetime

from pydantic import BaseModel

from app.models.order import OrderStatus


class ArtisanOut(BaseModel):
    id: int
    user_id: int
    name: str
    specialty: str | None = None
    monthly_capacity: int
    bio: str | None = None
    avatar_url: str | None = None
    average_rating: float
    review_count: int

    class Config:
        from_attributes = True


class ArtisanScheduleOut(BaseModel):
    id: int
    artisan_id: int
    year_month: int
    assigned_count: int
    capacity: int
    version: int

    class Config:
        from_attributes = True


class ArtisanTaskOut(BaseModel):
    order_id: int
    order_no: str
    status: OrderStatus
    assigned_at: datetime
    deadline: datetime | None = None
