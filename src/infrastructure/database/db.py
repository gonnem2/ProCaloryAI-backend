from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.settings import settings

async_engine = create_async_engine(
    url=settings.db_settings.dsn,
    pool_size=20,
    max_overflow=10,
    pool_timeout=60,
)


Session = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
