from fastapi import (
    APIRouter,
    Depends,
    Request,
    HTTPException,
    responses,
    status
)
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.security.utils import get_authorization_scheme_param

from ..services.posts import PostService
from ..services.auth import get_current_user
from .forms import PostForm
from ..schemas import User

templates = Jinja2Templates(directory="src/blog/api/templates/")
router = APIRouter()


@router.get('/', response_class=HTMLResponse)
def index(request: Request, post_service: PostService = Depends(), msg: str = None):
    posts = post_service.get_posts()
    token = request.cookies.get('access_token')
    if token:
        user = get_current_user(token=token)
    else:
        user = None
    return templates.TemplateResponse('posts/index.html', {'request': request,
                                                           'posts': posts,
                                                           'msg': msg,
                                                           'user': user})


@router.post('/{post_id}/delete')
def delete_post(request: Request, post_id: int, post_service: PostService = Depends()):
    post_service.delete_post(post_id=post_id)
    return templates.TemplateResponse('posts/delete_post.html', {'request': request})


@router.get("/create_post")
def create_post(request: Request):
    return templates.TemplateResponse("posts/create_post.html", {"request": request})


@router.post("/create_post/")
async def create_post(request: Request, post_service: PostService = Depends()):
    form = PostForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            token = request.cookies.get("access_token")
            current_user: User = get_current_user(token=token)
            post_service.create_post(data=form.data(), user_id=current_user.id)
            form.__dict__.update(msg="Запись успешно добавилась")
            return responses.RedirectResponse("/", status_code=status.HTTP_302_FOUND)
        except Exception as e:
            print(e)
            form.__dict__.get("errors").append("Вы не вошли в аккаунт")
            return templates.TemplateResponse("posts/create_post.html", form.__dict__)
    return templates.TemplateResponse("posts/create_post.html", form.__dict__, )


@router.get('/{post_id}')
def post_detail(request: Request, post_id: int, post_service: PostService = Depends()):
    post = post_service.get_post(post_id=post_id)
    return templates.TemplateResponse('posts/detail_post.html', {'request': request,
                                                                 'post': post})
