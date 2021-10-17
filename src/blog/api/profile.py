from fastapi import (
    APIRouter,
    Request,
    Depends,
)
from fastapi.templating import Jinja2Templates

from ..schemas import User
from ..services.auth import get_current_user

templates = Jinja2Templates(directory="src/blog/api/templates/")
router = APIRouter()


@router.get("/profile/")
def profile(request: Request, user: User = Depends(get_current_user)):
    print('dsadsa', user.username)
    return templates.TemplateResponse("profile/profile.html", {"request": request, 'user': user})
