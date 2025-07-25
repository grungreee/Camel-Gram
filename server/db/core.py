from sqlalchemy import select, Column
from server.db.models import metadata_obj, users_table
from server.db.database import sync_engine, async_engine
from typing import Any


def create_tables() -> None:
    metadata_obj.create_all(sync_engine)


async def insert_username(username: str, password: str, email: str) -> None:
    async with async_engine.begin() as conn:
        smtp = users_table.insert().values(username=username, password=password, email=email)
        await conn.execute(smtp)


async def select_users_fields(*fields: Column[Any]) -> list[str]:
    async with async_engine.connect() as conn:
        smtp = select(*fields).select_from(users_table)
        result = await conn.execute(smtp)

    return result.all()


