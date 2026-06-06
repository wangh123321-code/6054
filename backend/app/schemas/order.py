from datetime import datetime

from pydantic import BaseModel

from app.models.order import OrderStatus


class OrderCreate(BaseModel):
    product_id: int
    total_price: float
    custom_size: str | None = None
    custom_color: str | None = None
    custom_message: str | None = None
    reference_image_url: str | None = None
    is_original: bool = False


class OrderAssign(BaseModel):
    artisan_id: int
    deadline: datetime | None = None


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderProgressPhotoOut(BaseModel):
    id: int
    order_id: int
    uploaded_by: int
    image_url: str
    description: str | None = None
    uploaded_at: datetime

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: int
    order_no: str
    customer_id: int
    product_id: int
    status: OrderStatus
    total_price: float
    custom_size: str | None = None
    custom_color: str | None = None
    custom_message: str | None = None
    reference_image_url: str | None = None
    is_original: bool
    version: int
    created_at: datetime
    updated_at: datetime
    assignments: list = []
    progress_photos: list[OrderProgressPhotoOut] = []

    class Config:
        from_attributes = True
