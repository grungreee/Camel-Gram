from app.schemas import AccountData
import uuid

TEST: bool = False
LOCAL: bool = True

HOST: str = "localhost:8000" if LOCAL else "camel-gram.onrender.com"

API_URL: str = f"http://{HOST}" if LOCAL else f"https://{HOST}"
WS_URL: str = f"ws://{HOST}" if LOCAL else f"wss://{HOST}"

session: str = "" if not TEST else str(uuid.uuid1())
version: str = "1.0.0"
account_data: AccountData | None = None
