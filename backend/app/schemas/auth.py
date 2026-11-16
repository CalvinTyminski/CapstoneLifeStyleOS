
from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[A-Za-z0-9_]+$",
    )
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(
        min_length=8,
        max_length=128,
    )


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
