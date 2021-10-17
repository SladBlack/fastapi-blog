from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = 'users'
    id = sa.Column(sa.Integer, primary_key=True)
    email = sa.Column(sa.Text, unique=True)
    username = sa.Column(sa.Text)
    password_hash = sa.Column(sa.Text)
    is_banned = sa.Column(sa.Boolean, default=False)
    is_superuser = sa.Column(sa.Boolean, default=False)

    posts = relationship("Post", backref="user")
    comments = relationship("Comment", backref="user")


class Post(Base):
    __tablename__ = 'posts'
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    title = sa.Column(sa.String(128))
    body = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    view_count = sa.Column(sa.Integer, default=0)
    like_count = sa.Column(sa.Integer, default=0)

    comments = relationship("Comment", backref="post")

    def __repr__(self):
        return self.title


class Comment(Base):
    __tablename__ = 'comments'
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    post_id = sa.Column(sa.Integer, sa.ForeignKey('posts.id'))
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    body = sa.Column(sa.String)

    def __repr__(self):
        return self.user_id
