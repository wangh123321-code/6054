from datetime import datetime

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderStatus, OrderAssignment, OrderProgressPhoto, Review
from app.models.product import Product
from app.models.artisan import Artisan, ArtisanSchedule
from app.models.user import User
from app.tasks.notifications import send_order_status_notification
from app.tasks.reviews import recalculate_artisan_rating


async def create_order(db: AsyncSession, customer_id: int, order_data: dict) -> Order:
    product = await db.get(Product, order_data["product_id"])
    if not product:
        raise ValueError("产品不存在")

    stmt = (
        update(Product)
        .where(
            Product.id == product.id,
            Product.version == product.version,
            Product.stock > 0,
        )
        .values(stock=Product.stock - 1, version=Product.version + 1)
    )
    result = await db.execute(stmt)
    if result.rowcount == 0:
        raise ValueError("库存不足或产品已被修改，请重试")

    now = datetime.utcnow()
    order_no = f"PC{now.strftime('%Y%m%d%H%M%S')}{customer_id:06d}"

    order = Order(
        order_no=order_no,
        customer_id=customer_id,
        product_id=order_data["product_id"],
        status=OrderStatus.pending,
        total_price=order_data["total_price"],
        custom_size=order_data.get("custom_size"),
        custom_color=order_data.get("custom_color"),
        custom_message=order_data.get("custom_message"),
        reference_image_url=order_data.get("reference_image_url"),
        is_original=order_data.get("is_original", False),
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order


async def update_order_status(db: AsyncSession, order_id: int, new_status: OrderStatus) -> Order:
    order = await db.get(Order, order_id)
    if not order:
        raise ValueError("订单不存在")

    order.status = new_status
    order.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(order)

    send_order_status_notification.delay(order.customer_id, order.order_no, new_status.value)
    return order


async def assign_artisan(db: AsyncSession, order_id: int, artisan_id: int, deadline: datetime | None = None) -> OrderAssignment:
    order = await db.get(Order, order_id)
    if not order:
        raise ValueError("订单不存在")

    now = datetime.utcnow()
    year_month = int(now.strftime("%Y%m"))

    schedule = await db.execute(
        select(ArtisanSchedule).where(
            ArtisanSchedule.artisan_id == artisan_id,
            ArtisanSchedule.year_month == year_month,
        )
    )
    schedule_obj = schedule.scalar_one_or_none()

    if not schedule_obj:
        from app.models.artisan import Artisan
        artisan = await db.get(Artisan, artisan_id)
        if not artisan:
            raise ValueError("匠人不存在")
        schedule_obj = ArtisanSchedule(
            artisan_id=artisan_id,
            year_month=year_month,
            assigned_count=0,
            capacity=artisan.monthly_capacity,
            version=1,
        )
        db.add(schedule_obj)
        await db.flush()

    stmt = (
        update(ArtisanSchedule)
        .where(
            ArtisanSchedule.id == schedule_obj.id,
            ArtisanSchedule.version == schedule_obj.version,
            ArtisanSchedule.assigned_count < ArtisanSchedule.capacity,
        )
        .values(
            assigned_count=ArtisanSchedule.assigned_count + 1,
            version=ArtisanSchedule.version + 1,
        )
    )
    result = await db.execute(stmt)
    if result.rowcount == 0:
        raise ValueError("匠人当月产能已满")

    assignment = OrderAssignment(
        order_id=order_id,
        artisan_id=artisan_id,
        assigned_at=now,
        deadline=deadline,
    )
    db.add(assignment)

    order.status = OrderStatus.assigned
    order.updated_at = now
    await db.commit()
    await db.refresh(assignment)

    send_order_status_notification.delay(order.customer_id, order.order_no, OrderStatus.assigned.value)
    return assignment


async def add_progress_photo(db: AsyncSession, order_id: int, uploaded_by: int, image_url: str, description: str | None = None) -> OrderProgressPhoto:
    photo = OrderProgressPhoto(
        order_id=order_id,
        uploaded_by=uploaded_by,
        image_url=image_url,
        description=description,
    )
    db.add(photo)
    await db.commit()
    await db.refresh(photo)
    return photo


async def confirm_receipt(db: AsyncSession, order_id: int, customer_id: int) -> Order:
    order = await db.get(Order, order_id)
    if not order:
        raise ValueError("订单不存在")
    if order.customer_id != customer_id:
        raise ValueError("无权确认此订单")
    if order.status != OrderStatus.shipped:
        raise ValueError("订单状态不允许确认收货")

    order.status = OrderStatus.awaiting_review
    order.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(order)

    send_order_status_notification.delay(order.customer_id, order.order_no, OrderStatus.awaiting_review.value)
    return order


async def create_review(db: AsyncSession, order_id: int, customer_id: int, rating: int, comment: str | None = None) -> Review:
    if rating < 1 or rating > 5:
        raise ValueError("评分必须在1-5星之间")

    order = await db.get(Order, order_id)
    if not order:
        raise ValueError("订单不存在")
    if order.customer_id != customer_id:
        raise ValueError("无权评价此订单")
    if order.status != OrderStatus.awaiting_review:
        raise ValueError("订单状态不允许评价")

    existing_review = await db.execute(select(Review).where(Review.order_id == order_id))
    if existing_review.scalar_one_or_none():
        raise ValueError("此订单已评价过")

    stmt = select(OrderAssignment).where(OrderAssignment.order_id == order_id)
    result = await db.execute(stmt)
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise ValueError("订单未分配匠人，无法评价")

    review = Review(
        order_id=order_id,
        product_id=order.product_id,
        artisan_id=assignment.artisan_id,
        customer_id=customer_id,
        rating=rating,
        comment=comment,
    )
    db.add(review)

    order.status = OrderStatus.completed
    order.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(review)

    recalculate_artisan_rating.delay(assignment.artisan_id)
    send_order_status_notification.delay(order.customer_id, order.order_no, OrderStatus.completed.value)

    return review


async def get_reviews_by_product(db: AsyncSession, product_id: int, limit: int = 10) -> list[Review]:
    stmt = (
        select(Review, User)
        .join(User, Review.customer_id == User.id)
        .where(Review.product_id == product_id)
        .order_by(Review.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    reviews = []
    for review, user in result.all():
        review.customer_name = user.username
        reviews.append(review)
    return reviews


async def get_reviews_by_artisan(db: AsyncSession, artisan_id: int, limit: int = 20) -> list[Review]:
    stmt = (
        select(Review, User)
        .join(User, Review.customer_id == User.id)
        .where(Review.artisan_id == artisan_id)
        .order_by(Review.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    reviews = []
    for review, user in result.all():
        review.customer_name = user.username
        reviews.append(review)
    return reviews


async def get_review_by_order(db: AsyncSession, order_id: int) -> Review | None:
    stmt = select(Review).where(Review.order_id == order_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def calculate_artisan_rating(db: AsyncSession, artisan_id: int) -> None:
    stmt = select(
        func.avg(Review.rating).label("avg_rating"),
        func.count(Review.id).label("count")
    ).where(Review.artisan_id == artisan_id)
    result = await db.execute(stmt)
    row = result.mappings().first()

    avg_rating = float(row["avg_rating"] or 0)
    count = int(row["count"] or 0)

    artisan = await db.get(Artisan, artisan_id)
    if artisan:
        artisan.average_rating = round(avg_rating, 2)
        artisan.review_count = count
        await db.commit()
