from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Text, DateTime, Boolean, Index
from datetime import datetime


metadata_obj = MetaData(schema="camelgram_removeglad")

users_table = Table(
    "users",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("username", String),
    Column("display_name", String),
    Column("password", String),
    Column("email", String),
)

messages_table = Table(
    "messages",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("sender_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("receiver_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("message", Text, nullable=False),
    Column("timestamp", DateTime, default=datetime.now),
    Column("is_read", Boolean, default=False, nullable=False),
)

chats_table = Table(
    "chats",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("partner_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Index("unique_user_partner", "user_id", "partner_id", unique=True)
)
