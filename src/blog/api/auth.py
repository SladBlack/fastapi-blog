from datetime import timedelta

from fastapi import Depends, FastAPI, APIRouter, Request, HTTPException, Response, status, Form, responses
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..schemas import UserCreate, User, Token
from ..services.auth import AuthService, get_current_user
from .forms import LoginForm, UserCreateForm
from ..services.auth import AuthService
from ..settings import settings
from .utils import OAuth2PasswordBearerWithCookie

router = APIRouter(prefix='/auth')
templates = Jinja2Templates(directory="src/blog/templates")


@router.get("/sign-in")
def login(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/sign-in")
def login(request: Request, response: Response, auth_service: AuthService = Depends(),
          username: str = Form(...), password: str = Form(...)):
    try:
        access_token = auth_service.authenticate_user(username=username, password=password)
        response.set_cookie(key="access_token", value=access_token.access_token,
                            httponly=True)
        return {'status': 'ok'}
    except HTTPException:
        return {'status': 'bad'}


@router.get("/register/")
def register(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})


@router.post("/register/")
async def register(request: Request, auth_service: AuthService = Depends()):
    form = UserCreateForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            auth_service.register_new_user(email=form.email, username=form.username, password=form.password)
            return responses.RedirectResponse(
                "/?msg=Регистрация прошла успешно", status_code=status.HTTP_302_FOUND
            )
        except IntegrityError:
            form.__dict__.get("errors").append("Duplicate username or email")
            return templates.TemplateResponse("auth/register.html", form.__dict__)
    return templates.TemplateResponse("auth/register.html", form.__dict__)


@router.get("/logout")
def logout(response: Response, auth_service: AuthService = Depends()):
    auth_service.logout(response)
    return {'status': 'ok'}
