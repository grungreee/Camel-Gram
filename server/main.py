from server.db.core import create_tables, select_users_fields, insert_username
from server.schemas import RegisterRequest, RegisterResponse, VerifyCodeRequest, MessageResponse
from server.db.models import users_table
from server.utils import check_all, send_email
from redis.asyncio import Redis
from fastapi import FastAPI, HTTPException
import random
import secrets
import json

app = FastAPI()
redis = Redis(host="localhost", port=6379, decode_responses=True)

create_tables()


@app.post("/register")
async def register(user: RegisterRequest) -> RegisterResponse:
    all_usernames_and_emails: list[tuple] = await select_users_fields(users_table.c.username, users_table.c.email)
    usernames: set[str] = {row[0] for row in all_usernames_and_emails}
    emails: set[str] = {row[1] for row in all_usernames_and_emails}

    if user.username in usernames:
        raise HTTPException(status_code=400, detail="Username already exists.")
    if user.email in emails:
        raise HTTPException(status_code=400, detail="Email already used.")

    check_user: str | bool = check_all(user.username, user.password, user.email)

    if check_user is not True:
        raise HTTPException(status_code=400, detail=check_user)

    verify_code: str = "".join([str(random.randint(0, 9)) for _ in range(6)])
    temp_id: str = secrets.token_urlsafe(16)

    session_data: dict[str, str] = {
        "username": user.username,
        "password": user.password,
        "email": user.email
    }

    await redis.set(f"verify:{user.email}", verify_code, ex=300)
    await redis.set(f"session:{temp_id}", json.dumps(session_data), ex=300)

    await send_email(user.email, "Confirmation code", f"Your confirmation code is: {verify_code}\n"
                                                      f"Do not share it with anyone else. "
                                                      f"If you did not request this email, please ignore it.")

    return RegisterResponse(message="A confirmation code has been sent to your email address.", temp_id=temp_id)


@app.post("/verify_email")
async def verify_email(validation_data: VerifyCodeRequest) -> MessageResponse:
    session_data_raw = await redis.get(f"session:{validation_data.temp_id}")
    if not session_data_raw:
        raise HTTPException(status_code=400, detail="Invalid or expired token.")

    session_data: dict[str, str] = json.loads(session_data_raw)

    username: str = session_data["username"]
    password: str = session_data["password"]
    email: str = session_data["email"]

    code = await redis.get(f"verify:{email}")
    if not code or code != validation_data.code:
        raise HTTPException(status_code=400, detail="Invalid code.")

    await insert_username(username, password, email)

    await redis.delete(f"session:{validation_data.temp_id}")
    await redis.delete(f"verify:{email}")

    return MessageResponse(message="User registered successfully!")
