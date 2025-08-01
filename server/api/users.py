from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from server.db.models import users_table
from server.db.core import get_user_fields_by_id, search_username
from server.utils.jwt import verify_access_token

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
