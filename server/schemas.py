from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str


class RegisterResponse(MessageResponse):
    temp_id: str


class VerifyCodeRequest(BaseModel):
    code: str
    temp_id: str
