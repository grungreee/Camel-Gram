from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from server.utils.jwt import verify_access_token
from server.db.core import get_messages
from server.schemas import GetMessagesResponse

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.get("/messages")
async def messages(receiver_id: int, page: int, token: str = Depends(oauth2_scheme)) -> list[GetMessagesResponse]:
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    raw_messages = await get_messages(payload["user_id"], receiver_id, page)
    return [GetMessagesResponse(id=m[0], message=m[1], timestamp=m[2], sender_display_name=m[3]) for m in raw_messages]
