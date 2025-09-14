from pydantic import BaseModel
from datetime import datetime


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str


class RegisterRequest(LoginRequest):
    email: str


class RegisterResponse(BaseModel):
    temp_id: str


class VerifyCodeRequest(BaseModel):
    code: str
    temp_id: str


class DisplayNameChangeRequest(BaseModel):
    display_name: str


class MessagesResponse(BaseModel):
    message_id: int
    sender_id: int
    message: str
    timestamp: datetime
    display_name: str
    status: str


class GetMessagesResponse(BaseModel):
    messages: list[MessagesResponse]
    has_more: bool


class UserResponse(BaseModel):
    user_id: int
    username: str
    display_name: str


class GetChatsResponse(UserResponse):
    last_message: str
    timestamp: datetime
