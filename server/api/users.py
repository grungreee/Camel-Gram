from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from server.db.models import users_table
from server.db.core import get_user_fields_by_id
from server.utils.jwt import verify_access_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.get("/me")
async def me(token: str = Depends(oauth2_scheme)) -> dict:
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    row = await get_user_fields_by_id(payload["user_id"], users_table.c.username)
    return {"username": row[0]}
