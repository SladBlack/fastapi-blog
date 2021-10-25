from typing import Optional

from pydantic import BaseModel


class BaseUser(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None


class UserCreate(BaseUser):
    password: str


class User(BaseUser):
    id: Optional[int] = None
    is_superuser: Optional[bool] = None
    is_banned: Optional[bool] = None

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class UserProfile(BaseUser):
    is_superuser: str
