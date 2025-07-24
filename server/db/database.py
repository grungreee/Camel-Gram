from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import create_engine
from server.db.config import settings

sync_engine = create_engine(
    url=settings.database_url_psycopg,
    echo=False,
    pool_size=5,
    max_overflow=0
)

async_engine = create_async_engine(
    url=settings.database_url_asyncpg,
    echo=False,
    pool_size=5,
    max_overflow=0
)

