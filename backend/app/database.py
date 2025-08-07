from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from app.config import settings

# Check if using SQLite
is_sqlite = "sqlite" in settings.DATABASE_URL

# Async engine for FastAPI
if is_sqlite:
    # SQLite doesn't support these pool options
    async_engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True,
    )
else:
    # PostgreSQL with connection pooling
    async_engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True,
        pool_size=20,
        max_overflow=40,
        pool_pre_ping=True,
    )

# Sync engine for Alembic migrations
if is_sqlite:
    sync_engine = create_engine(
        settings.DATABASE_SYNC_URL,
        echo=False,
    )
else:
    sync_engine = create_engine(
        settings.DATABASE_SYNC_URL,
        echo=False,
        pool_size=20,
        max_overflow=40,
        pool_pre_ping=True,
    )

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Sync session factory for migrations
SessionLocal = sessionmaker(
    sync_engine,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()

# Dependency to get DB session
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()