from sqlalchemy import select, Column
from server.db.models import metadata_obj, users_table, messages_table
from server.db.database import sync_engine, async_engine
from typing import Any
from datetime import datetime


def create_tables() -> None:
    metadata_obj.create_all(sync_engine)


async def add_user(username: str, password: str, email: str) -> None:
    async with async_engine.begin() as conn:
        smtp = users_table.insert().values(display_name=username, username=username, password=password, email=email)
        await conn.execute(smtp)


async def get_user_fields(*fields: Column[Any]) -> list[tuple[str, str]]:
    async with async_engine.begin() as conn:
        smtp = select(*fields).select_from(users_table)
        result = await conn.execute(smtp)

    return result.all()


async def get_user_fields_by_id(user_id: int, *fields: Column[Any]) -> list[tuple[Any]] | None:
    async with async_engine.begin() as conn:
        # noinspection PyTypeChecker
        smtp = select(*fields).select_from(users_table).where(users_table.c.id == user_id)
        result = await conn.execute(smtp)

    return result.first()


async def get_user_data_by_username(username: str) -> tuple[str] | None:
    async with async_engine.begin() as conn:
        # noinspection PyTypeChecker
        smtp = select(users_table.c.id, users_table.c.password).where(users_table.c.username == username)
        result = await conn.execute(smtp)

    return result.first()


async def search_username(text: str) -> list[tuple[str, str, str]] | None:
    async with async_engine.begin() as conn:
        smtp = select(
            users_table.c.id,
            users_table.c.username,
            users_table.c.display_name
        ).where(users_table.c.username.like(f'%{text}%'))
        result = await conn.execute(smtp)

    return result.all()


async def change_display_name(user_id: int, new_display_name: str) -> None:
    async with async_engine.begin() as conn:
        smtp = users_table.update().where(users_table.c.id == user_id).values(display_name=new_display_name)
        await conn.execute(smtp)


async def insert_message(sender_id: int, receiver_id: int, message: str) -> None:
    async with async_engine.begin() as conn:
        smtp = messages_table.insert().values(sender_id=sender_id, receiver_id=receiver_id, message=message)
        await conn.execute(smtp)


async def get_messages(sender_id: int, receiver_id: int, page: int) -> list[tuple[int, str, datetime, str]]:
    async with async_engine.begin() as conn:
        # noinspection PyTypeChecker
        smtp = select(
            messages_table.c.id,
            messages_table.c.message,
            messages_table.c.timestamp,
            users_table.c.display_name
        ).join(users_table, users_table.c.id == messages_table.c.sender_id).where(
            ((messages_table.c.sender_id == sender_id) & (messages_table.c.receiver_id == receiver_id)) |
            ((messages_table.c.sender_id == receiver_id) & (messages_table.c.receiver_id == sender_id))
        ).order_by(messages_table.c.id.desc()).limit(20).offset(page * 20)

        result = await conn.execute(smtp)

    return result.all()
