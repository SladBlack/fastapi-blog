from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..database import get_session
from ..models import User


class ProfileService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    async def _get_user(self, user_id: int) -> User:
        user = await self.session.execute(select(User).where(User.id == user_id))
        return user.scalars().first()

    async def get_all_users(self):
        users = await self.session.execute(select(User))
        return users.scalars().all()

    async def block_user(self, user_id: int) -> None:
        user = await self._get_user(user_id=user_id)
        user.is_banned = True
        await self.session.commit()

    async def unblock_user(self, user_id: int) -> None:
        user = await self._get_user(user_id=user_id)
        user.is_banned = False
        await self.session.commit()
