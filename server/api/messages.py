from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from server.utils.jwt import verify_access_token
from server.db.core import get_messages_from_id, get_chats
from server.schemas import MessagesResponse, GetChatsResponse, GetMessagesResponse

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.get("/messages")
async def messages(receiver_id: int, message_id: int | None = None,
                   token: str = Depends(oauth2_scheme)) -> GetMessagesResponse:
    payload: dict | None = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    raw_messages, has_more = await get_messages_from_id(payload["user_id"], receiver_id, message_id)

    return GetMessagesResponse(messages=[MessagesResponse(message_id=m[0], message=m[1], timestamp=m[2],
                                                          display_name=m[3], status="read" if m[4] else "received")
                                         for m in raw_messages], has_more=has_more)


@router.get("/chats")
async def chats(token: str = Depends(oauth2_scheme)) -> list[GetChatsResponse]:
    payload: dict | None = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id: int = payload["user_id"]

    chats: list = await get_chats(user_id)

    if not chats:
        raise HTTPException(status_code=404, detail="No chats found")

    return [GetChatsResponse(user_id=chat[0], username=chat[1], display_name=chat[2],
                             last_message=chat[3], timestamp=chat[4]) for chat in chats]
