from sqlalchemy import select, Column
from server.db.models import metadata_obj, users_table
from server.db.database import sync_engine, async_engine
from typing import Any


def create_tables() -> None:
    metadata_obj.create_all(sync_engine)


def insert_username(username: str, password: str, email: str) -> None:
    with sync_engine.connect() as conn:
        smtp = users_table.insert().values(username=username, password=password, email=email)
        conn.execute(smtp)
        conn.commit()


async def select_users_fields(*fields: Column[Any]) -> list[str]:
    async with async_engine.connect() as conn:
        smtp = select(*fields).select_from(users_table)
        result = await conn.execute(smtp)

    return [row[0] for row in result.all()]
