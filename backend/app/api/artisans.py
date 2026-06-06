from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.artisan import Artisan, ArtisanSchedule
from app.models.order import Order, OrderAssignment, OrderStatus, Review
from app.models.user import User
from app.schemas.artisan import ArtisanOut, ArtisanScheduleOut, ArtisanTaskOut
from app.schemas.order import ReviewOut
from app.api.auth import get_current_user
from app.services.order import get_reviews_by_artisan

router = APIRouter(prefix="/api/artisans", tags=["匠人"])


async def _get_artisan_by_user(db: AsyncSession, user: User) -> Artisan:
    stmt = select(Artisan).where(Artisan.user_id == user.id)
    result = await db.execute(stmt)
    artisan = result.scalar_one_or_none()
    if not artisan:
        raise HTTPException(status_code=404, detail="匠人信息不存在")
    return artisan


@router.get("/my-schedule", response_model=list[ArtisanScheduleOut])
async def get_my_schedule(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    artisan = await _get_artisan_by_user(db, current_user)
    stmt = select(ArtisanSchedule).where(ArtisanSchedule.artisan_id == artisan.id).order_by(ArtisanSchedule.year_month)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/my-tasks", response_model=list[ArtisanTaskOut])
async def get_my_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    artisan = await _get_artisan_by_user(db, current_user)
    stmt = (
        select(OrderAssignment, Order)
        .join(Order, OrderAssignment.order_id == Order.id)
        .where(OrderAssignment.artisan_id == artisan.id)
        .order_by(OrderAssignment.assigned_at.desc())
    )
    result = await db.execute(stmt)
    tasks = []
    for assignment, order in result.all():
        tasks.append(ArtisanTaskOut(
            order_id=order.id,
            order_no=order.order_no,
            status=order.status,
            assigned_at=assignment.assigned_at,
            deadline=assignment.deadline,
        ))
    return tasks


@router.get("/{artisan_id}/schedule", response_model=list[ArtisanScheduleOut])
async def get_artisan_schedule(
    artisan_id: int,
    db: AsyncSession = Depends(get_db),
):
    artisan = await db.get(Artisan, artisan_id)
    if not artisan:
        raise HTTPException(status_code=404, detail="匠人不存在")

    stmt = select(ArtisanSchedule).where(ArtisanSchedule.artisan_id == artisan_id).order_by(ArtisanSchedule.year_month)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{artisan_id}/tasks", response_model=list[ArtisanTaskOut])
async def get_artisan_tasks(
    artisan_id: int,
    db: AsyncSession = Depends(get_db),
):
    artisan = await db.get(Artisan, artisan_id)
    if not artisan:
        raise HTTPException(status_code=404, detail="匠人不存在")

    stmt = (
        select(OrderAssignment, Order)
        .join(Order, OrderAssignment.order_id == Order.id)
        .where(OrderAssignment.artisan_id == artisan_id)
        .order_by(OrderAssignment.assigned_at.desc())
    )
    result = await db.execute(stmt)
    tasks = []
    for assignment, order in result.all():
        tasks.append(ArtisanTaskOut(
            order_id=order.id,
            order_no=order.order_no,
            status=order.status,
            assigned_at=assignment.assigned_at,
            deadline=assignment.deadline,
        ))
    return tasks


@router.get("/{artisan_id}", response_model=ArtisanOut)
async def get_artisan_detail(
    artisan_id: int,
    db: AsyncSession = Depends(get_db),
):
    artisan = await db.get(Artisan, artisan_id)
    if not artisan:
        raise HTTPException(status_code=404, detail="匠人不存在")
    return artisan


@router.get("/{artisan_id}/reviews", response_model=list[ReviewOut])
async def get_artisan_reviews(
    artisan_id: int,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    artisan = await db.get(Artisan, artisan_id)
    if not artisan:
        raise HTTPException(status_code=404, detail="匠人不存在")
    reviews = await get_reviews_by_artisan(db, artisan_id, limit)
    return reviews
