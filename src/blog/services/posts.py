from fastapi import (
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from ..database import get_session
from ..models import Post, Comment, Like
from ..schemas import CreatePost


class PostService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_post(self, post_id: int):
        post = self.session.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        return post

    def get_posts(self):
        posts = self.session.query(Post).all()

        if not posts:
            return []
        return posts

    def create_post(self, data: dict, user_id: int):
        post = Post(**data)
        post.user_id = user_id
        self.session.add(post)
        self.session.commit()
        return post

    def delete_post(self, post_id: int):
        post = self.get_post(post_id)
        self.session.delete(post)
        self.session.commit()

    def update_post(self, post_id: int, form):
        post = self.get_post(post_id)
        post.title = form.get('title')
        post.body = form.get('body')
        self.session.commit()

    def create_comment(self, post_id: int, body: str, user_id: int):
        comment = Comment(user_id=user_id,
                          body=body,
                          post_id=post_id)
        self.session.add(comment)
        self.session.commit()

    def get_comments(self, post_id):
        return self.session.query(Comment).filter(Comment.post_id == post_id)

    def delete_comment(self, comment_id: int) -> None:
        comment = self.session.query(Comment).filter(Comment.id == comment_id).first()
        self.session.delete(comment)
        self.session.commit()

    def like_post(self, post_id, user_id):
        like = self.session.query(Like).filter(Like.user_id == user_id, Like.post_id == post_id)
        if not like.first():
            like = Like(post_id=post_id, user_id=user_id)
            self.session.add(like)
        else:
            like.delete()
        self.session.commit()
