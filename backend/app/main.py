from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
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
    from app.models.product import Product, ProductCategory
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

        stmt = select(Product).limit(1)
        result = await session.execute(stmt)
        if not result.scalar_one_or_none():
            sample_products = [
                Product(
                    name="龙凤呈祥婚庆剪纸",
                    description="传统婚庆剪纸精品，龙凤图案栩栩如生，寓意吉祥如意、百年好合。采用高档红纸，手工精雕细琢。",
                    category=ProductCategory.wedding,
                    template_image_url="https://picsum.photos/seed/wedding1/400/400",
                    price_base=299.0,
                    is_template=True,
                    stock=50,
                ),
                Product(
                    name="百年好合喜字剪纸",
                    description="经典喜字剪纸，设计精美，线条流畅，是婚庆装饰的不二之选。可定制姓氏组合。",
                    category=ProductCategory.wedding,
                    template_image_url="https://picsum.photos/seed/wedding2/400/400",
                    price_base=159.0,
                    is_template=True,
                    stock=100,
                ),
                Product(
                    name="企业LOGO定制剪纸",
                    description="专业定制企业LOGO剪纸，完美展现品牌形象。适合企业年会、商务礼品、办公室装饰。",
                    category=ProductCategory.enterprise,
                    template_image_url="https://picsum.photos/seed/enterprise1/400/400",
                    price_base=599.0,
                    is_template=True,
                    stock=20,
                ),
                Product(
                    name="企业文化墙剪纸系列",
                    description="为企业量身打造的文化墙剪纸套装，融合企业价值观与传统剪纸艺术，提升企业文化品位。",
                    category=ProductCategory.enterprise,
                    template_image_url="https://picsum.photos/seed/enterprise2/400/400",
                    price_base=1299.0,
                    is_template=True,
                    stock=10,
                ),
                Product(
                    name="新春福字剪纸",
                    description="传统新春福字，笔法遒劲，寓意福到运来。春节家居装饰必备佳品。",
                    category=ProductCategory.festival,
                    template_image_url="https://picsum.photos/seed/festival1/400/400",
                    price_base=89.0,
                    is_template=True,
                    stock=200,
                ),
                Product(
                    name="元宵花灯剪纸套装",
                    description="元宵节特色花灯剪纸，图案精美，色彩鲜艳，营造浓厚节日氛围。",
                    category=ProductCategory.festival,
                    template_image_url="https://picsum.photos/seed/festival2/400/400",
                    price_base=199.0,
                    is_template=True,
                    stock=80,
                ),
                Product(
                    name="肖像剪纸定制",
                    description="根据照片定制专属肖像剪纸，匠心独运，栩栩如生。独一无二的艺术品，送礼佳品。",
                    category=ProductCategory.custom,
                    template_image_url="https://picsum.photos/seed/custom1/400/400",
                    price_base=399.0,
                    is_template=True,
                    stock=30,
                ),
                Product(
                    name="家族族谱剪纸",
                    description="定制家族族谱剪纸，传承家族文化，铭记家族历史。珍贵的家族传家宝。",
                    category=ProductCategory.custom,
                    template_image_url="https://picsum.photos/seed/custom2/400/400",
                    price_base=899.0,
                    is_template=True,
                    stock=15,
                ),
            ]
            session.add_all(sample_products)
            await session.commit()


app = FastAPI(title="莆田剪纸合作社在线商城", version="1.0.0", lifespan=lifespan)

cors_origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS else []
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
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
