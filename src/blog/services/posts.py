from typing import Optional

from fastapi import (
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import desc, func, select

from ..database import get_session
from ..models import Post, Comment, Like, View


class PostService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    async def get_post(self, post_id: int) -> Post:
        post = await self.session.execute(select(Post).where(Post.id == post_id))

        if not post:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        return post.scalars().first()

    async def get_detail_post(self, post_id: int, user_id: Optional[int] = None):
        post = await self.session.execute(select(Post).where(Post.id == post_id).options(selectinload(Post.users)))

        if user_id:
            views = await self.session.execute(select(View).where(View.post_id == post_id, View.user_id == user_id))
            if not views.scalars().first():
                self.session.add(View(user_id=user_id, post_id=post_id))
                await self.session.commit()

        return post.scalars().first()

    async def get_posts(self) -> list:
        posts = await self.session.execute(select(Post).options(selectinload(Post.likes),
                                                                selectinload(Post.views)))

        if not posts:
            return []
        return posts.scalars().all()

    async def create_post(self, data: dict, user_id: int) -> None:
        post = Post(**data)
        post.user_id = user_id
        self.session.add(post)
        await self.session.commit()

    async def delete_post(self, post_id: int):
        post = await self.get_post(post_id)
        await self.session.delete(post)
        await self.session.commit()

    async def update_post(self, post_id: int, form):
        post = await self.get_post(post_id)
        post.title = form.get('title')
        post.body = form.get('body')
        await self.session.commit()

    async def create_comment(self, post_id: int, body: str, user_id: int) -> str:
        comment = Comment(user_id=user_id,
                          body=body,
                          post_id=post_id)
        self.session.add(comment)
        await self.session.commit()
        return 'Комментарий успешно оставлен'

    async def get_comments(self, post_id: int):
        comments = await self.session.execute(
            select(Comment)
                .where(Comment.post_id == post_id)
                .options(selectinload(Comment.user))
        )
        return comments.scalars().all()

    async def delete_comment(self, comment_id: int) -> None:
        comment = await self.session.execute(select(Comment).where(Comment.id == comment_id))
        await self.session.delete(comment.scalars().first())
        await self.session.commit()

    async def like_post(self, post_id, user_id) -> str:
        likes = await self.session.execute(select(Like).where(Like.user_id == user_id, Like.post_id == post_id))
        like = likes.scalars().first()
        if not like:
            self.session.add(Like(post_id=post_id, user_id=user_id))
            msg = 'Лайк поставлен'
        else:
            await self.session.delete(like)
            msg = 'Лайк удален'
        await self.session.commit()
        return msg

    async def get_sort_posts(self, sort: Optional[str]):
        sort_functions = {'by_newest_date': self._sort_by_newest_date,
                          'by_oldest_date': self._sort_by_oldest_date,
                          'by_popular': self._sort_by_popular,
                          'by_views': self._sort_by_views,
                          None: self.get_posts
                          }
        return await sort_functions.get(sort)()

    async def _sort_by_newest_date(self):
        posts = await self.session.execute(select(Post)
                                           .order_by(Post.created_at.desc())
                                           .options(selectinload(Post.likes),
                                                    selectinload(Post.views)))
        return posts.scalars().all()

    async def _sort_by_oldest_date(self):
        posts = await self.session.execute(select(Post)
                                           .order_by(Post.created_at)
                                           .options(selectinload(Post.likes),
                                                    selectinload(Post.views)))
        return posts.scalars().all()

    async def _sort_by_popular(self):
        posts = await self.session.execute(select(Post)
                                           .outerjoin(Like)
                                           .group_by(Post.id)
                                           .order_by(desc(func.count(Like.user_id)))
                                           .options(selectinload(Post.likes),
                                                    selectinload(Post.views)))
        return posts.scalars().all()

    async def _sort_by_views(self):
        posts = await self.session.execute(select(Post)
                                           .outerjoin(View)
                                           .group_by(Post.id)
                                           .order_by(desc(func.count(View.user_id)))
                                           .options(selectinload(Post.likes),
                                                    selectinload(Post.views)))
        return posts.scalars().all()
