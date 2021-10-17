from datetime import date
from typing import Optional

from pydantic import BaseModel


class PostBase(BaseModel):
    title: str
    body: str


class Post(BaseModel):
    pass

    class Config:
        orm_mode = True


class CreatePost(PostBase):
    pass


class Comment(BaseModel):
    body: str
