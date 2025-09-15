from app.schemas import AccountData
import uuid

local: bool = False
test: bool = False
session: str = "" if not test else uuid.uuid1()
url: str = "localhost:8000" if local else "https://camel-gram.onrender.com"
version: str = "1.0.0"
account_data: AccountData | None = None
