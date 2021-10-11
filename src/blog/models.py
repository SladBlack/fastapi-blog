from datetime import datetime

import sqlalchemy as sa

from .database import Base


class User(Base):
    __tablename__ = 'users'
    id = sa.Column(sa.Integer, primary_key=True)
    email = sa.Column(sa.Text, unique=True)
    username = sa.Column(sa.Text)
    password_hash = sa.Column(sa.Text)
    is_banned = sa.Column(sa.Boolean, default=False)
    is_superuser = sa.Column(sa.Boolean, default=False)


class Post(Base):
    __tablename__ = 'posts'
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    title = sa.Column(sa.String(128))
    body = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    view_count = sa.Column(sa.Integer, default=0)

    def __repr__(self):
        return self.title
