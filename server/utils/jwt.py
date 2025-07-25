import dotenv
import os
from jose import JWTError, jwt
from datetime import datetime, timedelta, UTC

dotenv.load_dotenv(r"C:\Users\PC\PycharmProjects\CamelGram\server\.env")

SECRET_KEY = os.getenv("JWT_KEY")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")


def verify_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        return None
