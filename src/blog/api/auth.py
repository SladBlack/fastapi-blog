from fastapi import Depends, FastAPI, APIRouter, Request, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..schemas import UserCreate, User, Token
from ..services.auth import AuthService, get_current_user
from .forms import LoginForm
from ..services.auth import AuthService

router = APIRouter(prefix='/auth')
templates = Jinja2Templates(directory="src/blog/api/templates")


@router.post('/sign-up', response_model=Token)
def sign_up(user_data: UserCreate, service: AuthService = Depends()):
    return service.register_new_user(user_data)


# @router.post('/sign-in', response_model=Token)
# def sign_in(form_data: OAuth2PasswordRequestForm = Depends(),
#             service: AuthService = Depends()):
#     return service.authenticate_user(form_data.username,
#                                      form_data.password)


@router.get('/user', response_model=User)
def get_user(user: User = Depends(get_current_user)):
    return user


@router.get("/sign-in/")
def login(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/sign-in/")
async def login(request: Request, auth_service: AuthService = Depends()):
    form = LoginForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            form.__dict__.update(msg="Вход выполнен успешно")
            response = templates.TemplateResponse("auth/login.html", form.__dict__)
            auth_service.authenticate_user(username=form.username, password=form.password)
            return response
        except HTTPException:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append("Неверное имя или пароль")
            return templates.TemplateResponse("auth/login.html", form.__dict__)
    return templates.TemplateResponse("auth/login.html", form.__dict__)
