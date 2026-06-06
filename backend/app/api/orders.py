from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.order import Order, OrderStatus, OrderAssignment, OrderProgressPhoto, Review
from app.models.artisan import Artisan
from app.models.user import User
from app.schemas.order import OrderCreate, OrderOut, OrderAssign, OrderStatusUpdate, OrderProgressPhotoOut, ReviewCreate, ReviewOut
from app.api.auth import get_current_user, require_artisan_or_admin
from app.services.order import create_order, update_order_status, assign_artisan, add_progress_photo, confirm_receipt, create_review, get_review_by_order

router = APIRouter(prefix="/api/orders", tags=["订单"])


async def _get_order_with_relations(db: AsyncSession, order_id: int) -> Order | None:
    stmt = select(Order).options(
        selectinload(Order.assignments),
        selectinload(Order.progress_photos)
    ).where(Order.id == order_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


@router.post("", response_model=OrderOut, status_code=201)
async def place_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        order = await create_order(db, current_user.id, order_data.model_dump())
        return await _get_order_with_relations(db, order.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[OrderOut])
async def list_my_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Order).options(
        selectinload(Order.assignments),
        selectinload(Order.progress_photos)
    ).where(Order.customer_id == current_user.id).order_by(Order.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    order = await _get_order_with_relations(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.customer_id != current_user.id and current_user.role.value not in ("admin", "artisan"):
        raise HTTPException(status_code=403, detail="无权查看此订单")
    return order


@router.put("/{order_id}/status", response_model=OrderOut)
async def change_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role.value not in ("admin", "artisan"):
        raise HTTPException(status_code=403, detail="无权修改订单状态")
    try:
        await update_order_status(db, order_id, status_data.status)
        return await _get_order_with_relations(db, order_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/assign", response_model=OrderOut)
async def assign_order_artisan(
    order_id: int,
    assign_data: OrderAssign,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    try:
        await assign_artisan(db, order_id, assign_data.artisan_id, assign_data.deadline)
        return await _get_order_with_relations(db, order_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/progress-photo", response_model=OrderProgressPhotoOut, status_code=201)
async def upload_progress_photo(
    order_id: int,
    image_url: str = Form(...),
    description: str = Form(None),
    current_user: User = Depends(require_artisan_or_admin),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Artisan).where(Artisan.user_id == current_user.id)
    result = await db.execute(stmt)
    artisan = result.scalar_one_or_none()
    artisan_id = artisan.id if artisan else 0

    try:
        photo = await add_progress_photo(db, order_id, artisan_id, image_url, description)
        return photo
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{order_id}/progress-photos", response_model=list[OrderProgressPhotoOut])
async def get_progress_photos(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(OrderProgressPhoto).where(OrderProgressPhoto.order_id == order_id).order_by(OrderProgressPhoto.uploaded_at)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/{order_id}/confirm-receipt", response_model=OrderOut)
async def confirm_order_receipt(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        await confirm_receipt(db, order_id, current_user.id)
        return await _get_order_with_relations(db, order_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/review", response_model=ReviewOut, status_code=201)
async def submit_order_review(
    order_id: int,
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        review = await create_review(db, order_id, current_user.id, review_data.rating, review_data.comment)
        review.customer_name = current_user.username
        return review
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{order_id}/review", response_model=ReviewOut | None)
async def get_order_review(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.customer_id != current_user.id and current_user.role.value not in ("admin", "artisan"):
        raise HTTPException(status_code=403, detail="无权查看此评价")
    review = await get_review_by_order(db, order_id)
    if review:
        user = await db.get(User, review.customer_id)
        review.customer_name = user.username if user else None
    return review
