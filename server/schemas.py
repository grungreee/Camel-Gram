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


class GetMessagesResponse(BaseModel):
    id: int
    message: str
    timestamp: datetime
    sender_display_name: str
