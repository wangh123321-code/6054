import asyncio

from app.tasks import celery_app


STATUS_MESSAGES = {
    "pending": "您的订单已创建，等待处理",
    "assigned": "您的订单已分配匠人，即将开始制作",
    "in_progress": "您的订单正在制作中",
    "qc": "您的订单正在进行质量检验",
    "shipped": "您的订单已发货",
    "awaiting_review": "您的订单已确认收货，快去评价吧",
    "completed": "您的订单已完成",
    "cancelled": "您的订单已取消",
}


@celery_app.task
def send_order_status_notification(user_id: int, order_no: str, status: str):
    from app.database import async_session
    from app.services.notification import create_notification

    title = f"订单状态更新 - {order_no}"
    content = STATUS_MESSAGES.get(status, f"您的订单 {order_no} 状态已更新为 {status}")

    async def _create():
        async with async_session() as session:
            await create_notification(session, user_id, title, content)

    asyncio.run(_create())
