from sqlalchemy import Table, Column, Integer, String, MetaData


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
