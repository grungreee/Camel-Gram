from app.schemas import AccountData
import time

local: bool = True
test: bool = True
session: str = "" if not test else time.time()
url: str = "localhost:8000" if local else ""
version: str = "1.0.0"
account_data: AccountData | None = None
