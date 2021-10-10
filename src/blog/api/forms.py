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
