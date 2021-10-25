from fastapi import (
    Depends,
    APIRouter,
    Request,
    HTTPException,
    Response,
    status,
    responses,
)

from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError

from .forms import LoginForm, UserCreateForm
from ..services.auth import AuthService

router = APIRouter(prefix='/auth')
templates = Jinja2Templates(directory="src/blog/templates")


@router.get("/sign-in")
def login(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/sign-in")
async def login(request: Request, response: Response, auth_service: AuthService = Depends()):
    form = LoginForm(request)
    await form.load_data()
    try:
        access_token = await auth_service.authenticate_user(username=form.username, password=form.password)
        response.set_cookie(key="access_token", value=access_token.access_token, httponly=True)
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
    if form.is_valid():
        try:
            await auth_service.register_new_user(email=form.email, username=form.username, password=form.password)
            return responses.RedirectResponse("/?msg=Регистрация прошла успешно", status_code=status.HTTP_302_FOUND)
        except IntegrityError:
            form.__dict__.get("errors").append("Такой пользователь уже существует")
            return templates.TemplateResponse("auth/register.html", form.__dict__)
    return templates.TemplateResponse("auth/register.html", form.__dict__)


@router.get("/logout")
def logout(response: Response, auth_service: AuthService = Depends()):
    auth_service.logout(response)
    return {'status': 'ok'}
