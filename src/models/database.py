from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config.settings import settings

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # 开发模式下打印 SQL
    future=True
)

# 创建异步 Session 工厂
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    """依赖注入获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

