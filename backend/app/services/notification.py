from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


async def create_notification(db: AsyncSession, user_id: int, title: str, content: str | None = None) -> Notification:
    notification = Notification(
        user_id=user_id,
        title=title,
        content=content,
    )
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification


async def mark_as_read(db: AsyncSession, notification_id: int, user_id: int) -> bool:
    stmt = (
        update(Notification)
        .where(Notification.id == notification_id, Notification.user_id == user_id)
        .values(is_read=True)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


async def get_unread_count(db: AsyncSession, user_id: int) -> int:
    stmt = select(func.count(Notification.id)).where(
        Notification.user_id == user_id,
        Notification.is_read == False,
    )
    result = await db.execute(stmt)
    return result.scalar_one()
