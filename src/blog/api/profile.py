from fastapi import (
    APIRouter,
    Request,
    Depends,
    responses,
    status,
)
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from ..services.auth import get_user
from ..services.profile import ProfileService

templates = Jinja2Templates(directory="src/blog/templates/")
router = APIRouter()


@router.get("/profile")
async def profile(request: Request, profile_service: ProfileService = Depends(), msg: str = None, user=Depends(get_user)):
    users = await profile_service.get_all_users()
    return templates.TemplateResponse("profile/profile.html", {"request": request,
                                                               'user': user,
                                                               'users': users,
                                                               'msg': msg})


@router.post('/block_user/{user_id}', response_class=HTMLResponse)
async def block_user(user_id: int, profile_service: ProfileService = Depends()):
    await profile_service.block_user(user_id=user_id)
    return responses.RedirectResponse("/profile?msg=Пользователь забанен", status_code=status.HTTP_302_FOUND)


@router.post('/unblock_user/{user_id}', response_class=HTMLResponse)
async def unblock_user(user_id: int, profile_service: ProfileService = Depends()):
    await profile_service.unblock_user(user_id=user_id)
    return responses.RedirectResponse("/profile?msg=Пользователь разбанен", status_code=status.HTTP_302_FOUND)
