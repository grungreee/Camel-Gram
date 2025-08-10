from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from server.db.core import get_user_by_id, search_username, change_display_name
from server.utils.jwt import verify_access_token
from server.schemas import DisplayNameChangeRequest, UserResponse

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.get("/me")
async def me(token: str = Depends(oauth2_scheme)) -> UserResponse:
    payload: dict | None = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id: int = payload["user_id"]

    row: list | None = await get_user_by_id(user_id)

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(user_id=user_id, username=row[0], display_name=row[1])


@router.get("/search_user")
async def search_user(text: str, token: str = Depends(oauth2_scheme)) -> list[UserResponse]:
    payload: dict | None = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    rows = await search_username(text)

    if not rows:
        raise HTTPException(status_code=404, detail="User not found")

    response: list[UserResponse] = []

    for row in rows:
        if row[0] != payload["user_id"]:
            response.append(UserResponse(user_id=row[0], username=row[1], display_name=row[2]))
        if len(response) == 10:
            break

    if len(response) == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return response


@router.post("/change_display_name")
async def change_display_name_(body: DisplayNameChangeRequest, token: str = Depends(oauth2_scheme)) -> None:
    payload: dict | None = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    display_name: str = body.display_name.strip()

    if len(display_name) > 25 or len(display_name) < 1:
        raise HTTPException(status_code=400, detail="Password must be between 1 and 25 characters long")

    await change_display_name(payload["user_id"], display_name)
