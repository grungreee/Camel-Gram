from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(MessageResponse):
    token: str


class RegisterRequest(LoginRequest):
    email: str


class RegisterResponse(MessageResponse):
    temp_id: str


class VerifyCodeRequest(BaseModel):
    code: str
    temp_id: str


class DisplayNameChangeRequest(BaseModel):
    display_name: str


class MessageRequest(BaseModel):
    receiver_id: str
    message: str
