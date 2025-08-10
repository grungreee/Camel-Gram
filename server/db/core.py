from sqlalchemy import select, Column, case, func
from sqlalchemy.dialects.postgresql import insert
from server.db.models import metadata_obj, users_table, messages_table, chats_table
from server.db.database import sync_engine, async_engine
from typing import Any
from datetime import datetime


def create_tables() -> None:
    metadata_obj.create_all(sync_engine)


async def add_user(username: str, password: str, email: str) -> None:
    stmt = users_table.insert().values(display_name=username, username=username, password=password, email=email)

    async with async_engine.begin() as conn:
        await conn.execute(stmt)


async def get_user_fields(*fields: Column[Any]) -> list[tuple[str, str]]:
    stmt = select(*fields).select_from(users_table)

    async with async_engine.begin() as conn:
        result = await conn.execute(stmt)

    return result.all()


async def get_user_by_id(user_id: int) -> tuple[str, str] | None:
    # noinspection PyTypeChecker
    stmt = select(users_table.c.username, users_table.c.display_name).where(users_table.c.id == user_id)

    async with async_engine.begin() as conn:
        result = await conn.execute(stmt)

    return result.first()


async def get_user_data_by_username(username: str) -> tuple[int, str] | None:
    # noinspection PyTypeChecker
    stmt = select(users_table.c.id, users_table.c.password).where(users_table.c.username == username)

    async with async_engine.begin() as conn:
        result = await conn.execute(stmt)

    return result.first()


async def search_username(text: str) -> list[tuple[int, str, str]] | None:
    stmt = select(
        users_table.c.id,
        users_table.c.username,
        users_table.c.display_name
    ).where(users_table.c.username.like(f"%{text}%"))

    async with async_engine.begin() as conn:
        result = await conn.execute(stmt)

    return result.all()


async def change_display_name(user_id: int, new_display_name: str) -> None:
    stmt = users_table.update().where(users_table.c.id == user_id).values(display_name=new_display_name)

    async with async_engine.begin() as conn:
        await conn.execute(stmt)


async def insert_message(sender_id: int, receiver_id: int, message: str) -> None:
    stmt = messages_table.insert().values(sender_id=sender_id, receiver_id=receiver_id, message=message)

    async with async_engine.begin() as conn:
        await conn.execute(stmt)


async def get_messages(sender_id: int, receiver_id: int, page: int) -> list[tuple[int, str, datetime, str]]:
    # noinspection PyTypeChecker
    stmt = select(
        messages_table.c.id,
        messages_table.c.message,
        messages_table.c.timestamp,
        users_table.c.display_name
    ).join(users_table, users_table.c.id == messages_table.c.sender_id).where(
        ((messages_table.c.sender_id == sender_id) & (messages_table.c.receiver_id == receiver_id)) |
        ((messages_table.c.sender_id == receiver_id) & (messages_table.c.receiver_id == sender_id))
    ).order_by(messages_table.c.id.desc()).limit(20).offset(page * 20)

    async with async_engine.begin() as conn:
        result = await conn.execute(stmt)

    return result.all()


async def get_chats(user_id: int) -> list[tuple[int, str, str]]:
    # noinspection PyTypeChecker
    partner_case = case(
        (messages_table.c.sender_id == user_id, messages_table.c.receiver_id),
        else_=messages_table.c.sender_id
    )

    row_number = func.row_number().over(
        partition_by=partner_case,
        order_by=messages_table.c.timestamp.desc()
    ).label("rn")

    # noinspection PyTypeChecker
    messages_with_rank = select(
        messages_table.c.id,
        messages_table.c.sender_id,
        messages_table.c.receiver_id,
        messages_table.c.message,
        messages_table.c.timestamp,
        partner_case.label("partner_id"),
        row_number
    ).where(
        (messages_table.c.sender_id == user_id) | (messages_table.c.receiver_id == user_id)
    ).subquery()

    # noinspection PyTypeChecker
    stmt = (
        select(
            chats_table.c.partner_id,
            users_table.c.username,
            users_table.c.display_name,
            messages_with_rank.c.message,
            messages_with_rank.c.timestamp
        )
        .join(chats_table, chats_table.c.partner_id == users_table.c.id)
        .join(messages_with_rank, messages_with_rank.c.partner_id == chats_table.c.partner_id)
        .where(chats_table.c.user_id == user_id)
        .where(messages_with_rank.c.rn == 1)
    )

    async with async_engine.begin() as conn:
        result = await conn.execute(stmt)

    return result.all()


async def insert_chats(sender_id: int, receiver_id: int) -> None:
    stmt1 = insert(chats_table).values(user_id=sender_id, partner_id=receiver_id).on_conflict_do_nothing()
    stmt2 = insert(chats_table).values(user_id=receiver_id, partner_id=sender_id).on_conflict_do_nothing()

    async with async_engine.begin() as conn:
        await conn.execute(stmt1)
        await conn.execute(stmt2)
