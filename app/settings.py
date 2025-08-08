import random

local: bool = True
test: bool = True
session: str = str(random.randint(0, 999)) if test else ""
url: str = "localhost:8000" if local else ""
version: str = "1.0.0"
account_data: dict | None = None
