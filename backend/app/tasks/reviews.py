import asyncio

from app.tasks import celery_app


@celery_app.task
def recalculate_artisan_rating(artisan_id: int):
    from app.database import async_session
    from app.services.order import calculate_artisan_rating

    async def _recalculate():
        async with async_session() as session:
            await calculate_artisan_rating(session, artisan_id)

    asyncio.run(_recalculate())
