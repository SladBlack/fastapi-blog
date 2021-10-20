from typing import Optional

from fastapi import (
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from ..database import get_session
from ..models import Post, Comment, Like, View


class PostService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_post(self, post_id: int):
        post = self.session.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        return post

    def get_detail_post(self, post_id: int, user_id: Optional[int] = None):
        post = self.get_post(post_id=post_id)
        if user_id:
            view = self.session.query(View).filter(View.post_id == post_id, View.user_id == user_id).first()
            if not view:
                view = View(user_id=user_id, post_id=post_id)
                self.session.add(view)
                self.session.commit()
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

    def like_post(self, post_id, user_id) -> str:
        like = self.session.query(Like).filter(Like.user_id == user_id, Like.post_id == post_id)
        if not like.first():
            like = Like(post_id=post_id, user_id=user_id)
            self.session.add(like)
            msg = 'Лайк поставлен'
        else:
            like.delete()
            msg = 'Лайк удален'
        self.session.commit()
        return msg

    def sort(self, sort: str):
        if sort == 'by_newest_date':
            return self._sort_by_newest_date()
        elif sort == 'by_oldest_date':
            return self._sort_by_oldest_date()
        elif sort == 'by_popular':
            return self._sort_by_popular()
        elif sort == 'by_views':
            return self._sort_by_views()

    def _get_query_post(self):
        return self.session.query(Post)

    def _sort_by_newest_date(self):
        return self._get_query_post().order_by(desc(Post.created_at))

    def _sort_by_oldest_date(self):
        return self._get_query_post().order_by(Post.created_at)

    def _sort_by_popular(self):
        return self.session.query(Post, ) \
            .join(Like, isouter=True) \
            .group_by(Post.id) \
            .order_by(desc(func.count(Like.user_id))) \
            .all()

    def _sort_by_views(self):
        return self.session.query(Post) \
            .join(View, isouter=True) \
            .group_by(Post.id) \
            .order_by(desc(func.count(View.id))) \
            .all()
