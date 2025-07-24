from server.db.core import create_tables, select_users_fields
from server.schemas import RegisterRequest, MessageResponse
from server.db.models import users_table
from server.utils import check_all
from redis import Redis
from fastapi import FastAPI, HTTPException

app = FastAPI()
r = Redis(host="localhost", port=6379, decode_responses=True)

create_tables()


@app.post("/start_register")
async def start_register(user: RegisterRequest) -> MessageResponse:
    all_usernames_and_emails: list[tuple] = await select_users_fields(users_table.c.username, users_table.c.email)
    usernames: set[str] = {row[0] for row in all_usernames_and_emails}
    emails: set[str] = {row[1] for row in all_usernames_and_emails}

    if user.username in usernames:
        raise HTTPException(status_code=400, detail="Username already exists")
    if user.email in emails:
        raise HTTPException(status_code=400, detail="Email already exists")

    check_user: str | bool = check_all(user.username, user.password, user.email)

    if check_user is not True:
        raise HTTPException(status_code=400, detail=check_user)

    return MessageResponse(message="Success...")

