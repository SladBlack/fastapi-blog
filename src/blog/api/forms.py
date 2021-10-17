from typing import List
from typing import Optional

from fastapi import Request


class PostForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.title: Optional[str] = None
        self.body: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.title = form.get("title")
        self.body = form.get("body")

    async def is_valid(self):
        if len(self.title) < 5:
            self.errors.append("Заголовок должен содержать больше 5 символов")
        if not self.errors:
            return True
        return False

    def data(self):
        return {'title': self.title, 'body': self.body}

    def set_data(self, title, body):
        self.title = title
        self.body = body
        return self


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    def load_data(self):
        form = self.request.form
        self.username = form.get(
            "username"
        )  # since outh works on username field we are considering email as username
        self.password = form.get("password")

    def is_valid(self):
        if not self.username:
            self.errors.append("Email is required")
        if not self.password or not len(self.password) >= 4:
            self.errors.append("A valid password is required")
        if not self.errors:
            return True
        return False


class UserCreateForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.username: Optional[str] = None
        self.email: Optional[str] = None
        self.password: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.username = form.get("username")
        self.email = form.get("email")
        self.password = form.get("password")

    async def is_valid(self):
        if not self.username or not len(self.username) > 3:
            self.errors.append('Имя должно иметь больше трех символов')
        if not self.email or not (self.email.__contains__('@')):
            self.errors.append('Email обязателен')
        if not self.password or not len(self.password) >= 4:
            self.errors.append('Пароль должен состоять минимум из 4 символов')
        if not self.errors:
            return True
        return False


class CommentCreateForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.body: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.body = form.get("body")
