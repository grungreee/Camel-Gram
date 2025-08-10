from fastapi import APIRouter, HTTPException
from server.schemas import RegisterRequest, RegisterResponse, VerifyCodeRequest, LoginRequest, LoginResponse
from server.db.models import users_table
from server.db.core import get_user_fields, add_user, get_user_data_by_username
from server.utils.utils import check_all, send_email
from server.utils.jwt import create_access_token
from server.db.redis import redis
import json
import secrets
import random

router = APIRouter()


@router.post("/register")
async def register(user: RegisterRequest) -> RegisterResponse:
    all_users = await get_user_fields(users_table.c.username, users_table.c.email)
    usernames = {row[0] for row in all_users}
    emails = [row[1] for row in all_users]

    if user.username in usernames:
        raise HTTPException(status_code=400, detail="Username already exists.")
    if emails.count(user.email) > 3:
        raise HTTPException(status_code=400, detail="Email already used more than 3 times.")

    check = check_all(user.username, user.password, user.email)
    if check is not True:
        raise HTTPException(status_code=400, detail=check)

    verify_code = "".join([str(random.randint(0, 9)) for _ in range(6)])
    temp_id = secrets.token_urlsafe(16)

    await redis.set(f"verify:{user.email}", verify_code, ex=300)
    await redis.set(f"session:{temp_id}", json.dumps(user.model_dump()), ex=300)

    await send_email(user.email, "Confirmation code", f"Your code: {verify_code}")

    return RegisterResponse(temp_id=temp_id)


@router.post("/verify_email")
async def verify_email(data: VerifyCodeRequest) -> None:
    session_raw = await redis.get(f"session:{data.temp_id}")
    if not session_raw:
        raise HTTPException(status_code=400, detail="Session expired")

    session_data = json.loads(session_raw)
    code = await redis.get(f"verify:{session_data['email']}")

    if code != data.code:
        raise HTTPException(status_code=400, detail="Invalid code")

    await add_user(session_data["username"], session_data["password"], session_data["email"])
    await redis.delete(f"session:{data.temp_id}")
    await redis.delete(f"verify:{session_data['email']}")


@router.post("/login")
async def login(user: LoginRequest) -> LoginResponse:
    user_data_raw = await get_user_data_by_username(user.username)

    if (user_data_raw is None) or (not user_data_raw[1] or user_data_raw[1] != user.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    token = create_access_token({"user_id": user_data_raw[0]})
    return LoginResponse(token=token)
