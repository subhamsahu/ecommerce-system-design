from pydantic import BaseModel, ConfigDict, Field

from app.models import UserRole


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: str | None = Field(default=None, max_length=320)
    full_name: str | None = Field(default=None, max_length=200)
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.customer


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str | None
    full_name: str | None
    role: UserRole
    is_active: bool
    created_at: object


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse