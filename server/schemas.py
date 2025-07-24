from pydantic import BaseModel


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str


class VerifyCodeRequest(RegisterRequest):
    code: str


class MessageResponse(BaseModel):
    message: str
