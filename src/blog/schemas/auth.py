from typing import Optional

from pydantic import BaseModel


class BaseUser(BaseModel):
    email: Optional[str] = None
    username: str


class UserCreate(BaseUser):
    password: str


class User(BaseUser):
    id: int
    is_superuser: bool

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class UserProfile(BaseUser):
    is_superuser: str
