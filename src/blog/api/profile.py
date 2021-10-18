from fastapi import (
    APIRouter,
    Request,
    Depends,
    responses,
    status,
)
from fastapi.templating import Jinja2Templates

from ..services.auth import get_current_user
from ..services.profile import ProfileService

templates = Jinja2Templates(directory="src/blog/templates/")
router = APIRouter()


@router.get("/profile")
def profile(request: Request, profile_service: ProfileService = Depends(), msg: str = None):
    token = request.cookies.get('access_token')
    user = get_current_user(token)
    users = profile_service.get_all_users()
    return templates.TemplateResponse("profile/profile.html", {"request": request,
                                                               'user': user,
                                                               'users': users,
                                                               'msg': msg})


@router.post('/block_user/{user_id}')
def block_user(user_id: int, profile_service: ProfileService = Depends()):
    profile_service.block_user(user_id=user_id)
    return responses.RedirectResponse(f"/profile/?msg=Пользователь забанен", status_code=status.HTTP_302_FOUND)


@router.post('/unblock_user/{user_id}')
def unblock_user(user_id: int, profile_service: ProfileService = Depends()):
    profile_service.unblock_user(user_id=user_id)
    return responses.RedirectResponse(f"/profile/?msg=Пользователь разбанен", status_code=status.HTTP_302_FOUND)
