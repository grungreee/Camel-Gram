from sqlalchemy import select, Column, case, func, text
from server.db.models import metadata_obj, users_table, messages_table, chats_table
from server.db.database import sync_engine, async_engine
from typing import Any
from datetime import datetime


def create_tables() -> None:
    messages_table.drop(sync_engine, checkfirst=True)
    chats_table.drop(sync_engine, checkfirst=True)

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


async def insert_message(sender_id: int, receiver_id: int, message: str) -> tuple[int, datetime, str, str]:
    query = text("""
        WITH 
        inserted_message AS (
            INSERT INTO camelgram_removeglad.messages (sender_id, receiver_id, message, timestamp, is_read)
            VALUES (:sender_id, :receiver_id, :message, NOW(), FALSE)
            RETURNING id, timestamp, sender_id
        ),
        inserted_chats AS (
            INSERT INTO camelgram_removeglad.chats (user_id, partner_id)
            VALUES 
                (:sender_id, :receiver_id),
                (:receiver_id, :sender_id)
            ON CONFLICT (user_id, partner_id) DO NOTHING
        )
        SELECT 
            im.id,
            im.timestamp,
            u.username, 
            u.display_name
        FROM inserted_message im
        JOIN camelgram_removeglad.users u ON u.id = im.sender_id;
    """)

    async with async_engine.begin() as conn:
        result = await conn.execute(query, {
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "message": message
        })
        return result.first()


async def get_messages_from_id(sender_id: int, receiver_id: int,
                               from_message_id: int | None = None) -> list[tuple[int, str, datetime, str]]:
    # noinspection PyTypeChecker
    base_query = select(
        messages_table.c.id,
        messages_table.c.message,
        messages_table.c.timestamp,
        users_table.c.display_name,
        messages_table.c.is_read
    ).join(users_table, users_table.c.id == messages_table.c.sender_id).where(
        ((messages_table.c.sender_id == sender_id) & (messages_table.c.receiver_id == receiver_id)) |
        ((messages_table.c.sender_id == receiver_id) & (messages_table.c.receiver_id == sender_id))
    )

    stmt = base_query.where(messages_table.c.id < from_message_id) if from_message_id is not None else base_query
    stmt = stmt.order_by(messages_table.c.id.desc()).limit(20)

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
