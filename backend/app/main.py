from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.api.auth import router as auth_router
from app.api.products import router as products_router
from app.api.orders import router as orders_router
from app.api.artisans import router as artisans_router
from app.api.notifications import router as notifications_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await _create_initial_data()
    yield


async def _create_initial_data():
    from app.database import async_session
    from app.models.user import User, UserRole
    from app.services.auth import hash_password
    from sqlalchemy import select

    async with async_session() as session:
        stmt = select(User).where(User.username == "admin")
        result = await session.execute(stmt)
        if not result.scalar_one_or_none():
            admin = User(
                username="admin",
                email="admin@papercut.com",
                password_hash=hash_password("admin123"),
                role=UserRole.admin,
            )
            session.add(admin)
            await session.commit()


app = FastAPI(title="莆田剪纸合作社在线商城", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(orders_router)
app.include_router(artisans_router)
app.include_router(notifications_router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
