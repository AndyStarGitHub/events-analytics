import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from app.core.config import get_settings

settings = get_settings()
TESTING = os.getenv("TESTING") == "1"

engine_kwargs = {
    "echo": False,
    "pool_pre_ping": True,
}

if TESTING:
    engine_kwargs["poolclass"] = NullPool
    engine_kwargs["pool_pre_ping"] = False

engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
