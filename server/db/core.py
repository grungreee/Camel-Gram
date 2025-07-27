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


async def select_all_users_fields(*fields: Column[Any]) -> list[tuple[str, str]]:
    async with async_engine.connect() as conn:
        smtp = select(*fields).select_from(users_table)
        result = await conn.execute(smtp)

    return result.all()


async def get_user_fields_by_id(user_id: int, *fields: Column[Any]) -> list[tuple[Any]] | None:
    async with async_engine.connect() as conn:
        smtp = select(*fields).select_from(users_table).where(users_table.c.id == user_id)
        result = await conn.execute(smtp)

    return result.first()


async def get_user_by_username(username: str) -> tuple[str] | None:
    async with async_engine.connect() as conn:
        smtp = select(users_table.c.id, users_table.c.password).where(users_table.c.username == username)
        result = await conn.execute(smtp)

    return result.first()



