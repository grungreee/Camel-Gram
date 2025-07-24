from server.db.core import create_tables, select_users_fields
from server.schemas import RegisterRequest, VerifyCodeRequest, MessageResponse
from server.db.models import users_table
from server.utils import check_all, send_email
from redis.asyncio import Redis
from fastapi import FastAPI, HTTPException
import random
import time

app = FastAPI()
r = Redis(host="localhost", port=6379, decode_responses=True)

create_tables()


@app.post("/register")
async def register(user: RegisterRequest) -> MessageResponse:
    t = time.time()
    all_usernames_and_emails: list[tuple] = await select_users_fields(users_table.c.username, users_table.c.email)
    print(f"Time to select all users: {time.time() - t}")
    usernames: set[str] = {row[0] for row in all_usernames_and_emails}
    emails: set[str] = {row[1] for row in all_usernames_and_emails}

    if user.username in usernames:
        raise HTTPException(status_code=400, detail="Username already exists")
    if user.email in emails:
        raise HTTPException(status_code=400, detail="Email already used")

    check_user: str | bool = check_all(user.username, user.password, user.email)

    if check_user is not True:
        raise HTTPException(status_code=400, detail=check_user)

    verify_code: str = "".join([str(random.randint(0, 9)) for _ in range(6)])
    t = time.time()
    await r.setex(f"verify:{user.email}", 300, verify_code)
    print(f"Time to set key: {time.time() - t}")

    t = time.time()
    await send_email(user.email, "Confirmation code", f"Your confirmation code is: {verify_code}\n"
                                                      f"Do not share it with anyone else. "
                                                      f"If you did not request this email, please ignore it.")
    print(f"Time to send email: {time.time() - t}")

    return MessageResponse(message="A confirmation code has been sent to your email address.")


@app.post("/verify_email")
async def verify_email(user: VerifyCodeRequest) -> MessageResponse:
    pass
