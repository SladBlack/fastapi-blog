from datetime import datetime, timedelta
from typing import Optional, Union

from fastapi import HTTPException, status, Depends, Response, Request
from jose import jwt, JWTError
from passlib.hash import bcrypt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..schemas import User, Token, UserCreate
from ..settings import settings
from .. import models
from ..database import get_session
from ..api.utils import OAuth2PasswordBearerWithCookie

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/sign-in")


def get_current_user(token: str = Depends(oauth2_scheme)):
    return AuthService.validate_token(token)


def get_user(request: Request) -> Union[User, None]:
    token = request.cookies.get('access_token')
    if not token:
        return None
    return get_current_user(token)


class AuthService:
    @classmethod
    def verify_password(cls, plain_text: str, hashed_password: str) -> bool:
        return bcrypt.verify(plain_text, hashed_password)

    @classmethod
    def hash_password(cls, password: str) -> str:
        return bcrypt.hash(password)

    @classmethod
    def validate_token(cls, token: str) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm]
            )
        except JWTError:
            raise credentials_exception

        user_data = payload.get('user')

        try:
            user = User.parse_obj(user_data)
        except ValueError:
            raise credentials_exception
        return user

    @classmethod
    def create_token(cls, user: models.User) -> Token:
        user_data = User.from_orm(user)
        now = datetime.utcnow()
        payload = {
            'iat': now,
            'nbf': now,
            'exp': now + timedelta(seconds=settings.jwt_expiration),
            'sub': str(user_data.id),
            'user': user_data.dict(),
        }
        token = jwt.encode(
            payload,
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm
        )

        return Token(access_token=token)

    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    async def register_new_user(self, email: str, username: str, password: str) -> Token:
        user = models.User(
            email=email,
            username=username,
            password_hash=self.hash_password(password),
        )
        self.session.add(user)
        try:
            await self.session.commit()
            return self.create_token(user)
        except IntegrityError as ex:
            print(ex)
            await self.session.rollback()

    async def authenticate_user(self, username: str, password: str) -> Token:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        users = await self.session.execute(select(models.User).where(models.User.username == username))
        user = users.scalars().first()

        if not self.verify_password(password, user.password_hash):
            raise exception
        return self.create_token(user)

    @staticmethod
    def logout(response: Response):
        response.delete_cookie('access_token')
