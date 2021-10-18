from fastapi import (
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from ..database import get_session
from ..models import User


class ProfileService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def _get_user(self, user_id: int) -> User:
        return self.session.query(User).filter(User.id == user_id).first()

    def get_all_users(self):
        return self.session.query(User).all()

    def block_user(self, user_id: int):
        user = self._get_user(user_id=user_id)
        user.is_banned = True
        self.session.commit()

    def unblock_user(self, user_id: int):
        user = self._get_user(user_id=user_id)
        user.is_banned = False
        self.session.commit()
