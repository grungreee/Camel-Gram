from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from server.db.models import users_table
from server.db.core import get_user_fields_by_id, search_username, change_display_name
from server.utils.jwt import verify_access_token
from server.utils.utils import check_all
from server.schemas import DisplayNameChangeRequest, MessageResponse

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.get("/me")
async def me(token: str = Depends(oauth2_scheme)) -> dict:
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    row = await get_user_fields_by_id(payload["user_id"], users_table.c.username, users_table.c.display_name)

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    return {"username": row[0], "display_name": row[1]}


@router.get("/search_user")
async def search_user(text: str) -> dict:
    rows = await search_username(text)

    if not rows:
        raise HTTPException(status_code=404, detail="User not found")

    response: dict[str, list[dict[str, str]]] = {"users": []}

    for row in rows:
        response["users"].append({"username": row[0], "display_name": row[1]})
        if len(response["users"]) == 10:
            break

    return response


@router.post("/change_display_name")
async def change_display_name_(body: DisplayNameChangeRequest, token: str = Depends(oauth2_scheme)) -> MessageResponse:
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    display_name: str = body.display_name.strip()

    if len(display_name) > 25 or len(display_name) < 1:
        raise HTTPException(status_code=400, detail="Password must be between 1 and 25 characters long")

    await change_display_name(payload["user_id"], display_name)

    return MessageResponse(message="Display name changed successfully")
