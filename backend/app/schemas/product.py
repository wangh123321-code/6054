from datetime import datetime

from pydantic import BaseModel

from app.models.product import ProductCategory


class ProductImageOut(BaseModel):
    id: int
    product_id: int
    image_url: str
    sort_order: int

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    category: ProductCategory
    template_image_url: str | None = None
    price_base: float
    is_template: bool = True
    stock: int = 0


class ProductOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    category: ProductCategory
    template_image_url: str | None = None
    price_base: float
    is_template: bool
    stock: int
    version: int
    created_at: datetime
    images: list[ProductImageOut] = []

    class Config:
        from_attributes = True


class ProductListOut(BaseModel):
    id: int
    name: str
    category: ProductCategory
    template_image_url: str | None = None
    price_base: float
    is_template: bool
    stock: int

    class Config:
        from_attributes = True
