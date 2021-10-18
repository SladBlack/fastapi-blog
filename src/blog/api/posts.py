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

from ..services.posts import PostService
from ..services.auth import get_current_user
from .forms import PostForm, CommentCreateForm
from ..schemas import User, Token

templates = Jinja2Templates(directory="src/blog/templates/")
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


@router.get('/{post_id}/')
def post_detail(request: Request, post_id: int, post_service: PostService = Depends(), msg: str = None):
    post = post_service.get_post(post_id=post_id)
    form = CommentCreateForm(request)
    comments = post_service.get_comments(post_id=post_id)
    token = request.cookies.get('access_token')
    if token:
        user = get_current_user(token=token)
    else:
        user = None
    return templates.TemplateResponse('posts/detail_post.html', {'request': request,
                                                                 'post': post,
                                                                 'comment_form': form,
                                                                 'comments': comments,
                                                                 'msg': msg,
                                                                 'user': user})


@router.post('/{post_id}/')
async def post_detail(request: Request, post_id: int, post_service: PostService = Depends()):
    form = CommentCreateForm(request)
    await form.load_data()
    try:
        token = request.cookies.get("access_token")
        current_user = get_current_user(token=token)
        post_service.create_comment(body=form.body, user_id=current_user.id, post_id=post_id)
        return responses.RedirectResponse(f"/{post_id}/?msg=Комментарий оставлен", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        return responses.RedirectResponse(f"/{post_id}/?msg={e}", status_code=status.HTTP_302_FOUND)


@router.get("/create_post")
def create_post(request: Request):
    return templates.TemplateResponse("posts/create_post.html", {"request": request})


@router.post("/create_post")
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


@router.get('/update/{post_id}')
def update_post(request: Request, post_id: int, post_service: PostService = Depends()):
    post = post_service.get_post(post_id=post_id)
    form = PostForm(request)
    form = form.set_data(title=post.title, body=post.body)
    return templates.TemplateResponse('posts/update_post.html', {'request': request,
                                                                 'form': form,
                                                                 'post': post})


@router.post('/update_post/{post_id}')
async def update_post(request: Request, post_id: int, post_service: PostService = Depends()):
    form = PostForm(request)
    await form.load_data()
    if await form.is_valid():
        post_service.update_post(post_id=post_id, form=form.data())
        form.__dict__.update(msg="Изменения внесены успешно")
        return responses.RedirectResponse("/?msg=Изменения внесены успешно", status_code=status.HTTP_302_FOUND)
    else:
        form.__dict__.update(msg="Произошла ошибка")
        templates.TemplateResponse("posts/update_post.html", form.__dict__, )
    return templates.TemplateResponse("posts/update_post.html", form.__dict__, )


@router.post('/{post_id}/delete')
def delete_post(request: Request, post_id: int, post_service: PostService = Depends()):
    post_service.delete_post(post_id=post_id)
    return templates.TemplateResponse('posts/delete_post.html', {'request': request})


@router.post('/{comment_id}/delete_comment')
def delete_comment(comment_id: int, post_service: PostService = Depends()):
    post_service.delete_comment(comment_id=comment_id)
    return responses.RedirectResponse(f"/?msg=Комментарий удален", status_code=status.HTTP_302_FOUND)