from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.product import Product, ProductCategory
from app.models.order import Review
from app.schemas.product import ProductCreate, ProductOut, ProductListOut
from app.schemas.order import ReviewOut
from app.api.auth import require_admin
from app.services.order import get_reviews_by_product

router = APIRouter(prefix="/api/products", tags=["产品"])


@router.get("", response_model=list[ProductListOut])
async def list_products(
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Product)
    if category:
        try:
            cat_enum = ProductCategory(category)
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的产品分类")
        stmt = stmt.where(Product.category == cat_enum)
    stmt = stmt.order_by(Product.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Product).options(selectinload(Product.images)).where(Product.id == product_id)
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    return product


@router.post("", response_model=ProductOut, status_code=201)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_admin),
):
    product = Product(
        name=product_data.name,
        description=product_data.description,
        category=product_data.category,
        template_image_url=product_data.template_image_url,
        price_base=product_data.price_base,
        is_template=product_data.is_template,
        stock=product_data.stock,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    stmt = select(Product).options(selectinload(Product.images)).where(Product.id == product.id)
    result = await db.execute(stmt)
    return result.scalar_one()


@router.put("/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: int,
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_admin),
):
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")

    product.name = product_data.name
    product.description = product_data.description
    product.category = product_data.category
    product.template_image_url = product_data.template_image_url
    product.price_base = product_data.price_base
    product.is_template = product_data.is_template
    product.stock = product_data.stock
    await db.commit()
    stmt = select(Product).options(selectinload(Product.images)).where(Product.id == product_id)
    result = await db.execute(stmt)
    return result.scalar_one()


@router.get("/{product_id}/reviews", response_model=list[ReviewOut])
async def get_product_reviews(
    product_id: int,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    reviews = await get_reviews_by_product(db, product_id, limit)
    return reviews
