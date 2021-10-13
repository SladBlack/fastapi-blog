from datetime import timedelta

from fastapi import Depends, FastAPI, APIRouter, Request, HTTPException, Response, status, Form
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session


from ..schemas import UserCreate, User, Token
from ..services.auth import AuthService, get_current_user
from .forms import LoginForm
from ..services.auth import AuthService
from ..settings import settings
from .utils import OAuth2PasswordBearerWithCookie

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


@router.get('/cookie-test')
def set_cookie(response: Response):
    response.set_cookie(key='aboba', value='asdasdsa')
    return {'status': 'ok'}
