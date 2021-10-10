from datetime import datetime

import sqlalchemy as sa

from .database import Base


class Post(Base):
    __tablename__ = 'posts'
    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String(128))
    body = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    view_count = sa.Column(sa.Integer, default=0)

    def __repr__(self):
        return self.title
