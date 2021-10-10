from fastapi import (
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from ..database import get_session
from ..models import Post
from ..schemas import CreatePost


class ProductsService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def _get(self, post_id: int):
        post = self.session.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        return post

    def get_posts(self):
        posts = self.session.query(Post).all()

        if not posts:
            return []
        return posts

    def create_post(self, data: dict):
        post = Post(**data)
        self.session.add(post)
        self.session.commit()
        return post

    def delete_post(self, post_id: int):
        post = self._get(post_id)
        self.session.delete(post)
        self.session.commit()
