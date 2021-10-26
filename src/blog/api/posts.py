from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    Request,
    responses,
    status
)
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from ..services.posts import PostService
from ..services.auth import get_user
from .forms import PostForm, CommentCreateForm

templates = Jinja2Templates(directory="src/blog/templates/")
router = APIRouter()


@router.get('/', response_class=HTMLResponse)
async def index(request: Request, post_service: PostService = Depends(), msg: str = None, user=Depends(get_user),
                sort: Optional[str] = None):
    posts = await post_service.get_sort_posts(sort=sort)
    context = {
        'request': request,
        'posts': posts,
        'msg': msg,
        'user': user,
    }
    return templates.TemplateResponse('posts/index.html', context=context)


@router.get('/{post_id}/')
async def post_detail(request: Request, post_id: int, post_service: PostService = Depends(),
                      msg: str = None, user=Depends(get_user)):
    if user:
        user_id = user.id
    else:
        user_id = None

    post = await post_service.get_detail_post(post_id=post_id, user_id=user_id)
    comments = await post_service.get_comments(post_id=post_id)
    form = CommentCreateForm(request)
    context = {
        'request': request,
        'post': post,
        'comment_form': form,
        'comments': comments,
        'msg': msg,
        'user': user,
    }
    return templates.TemplateResponse('posts/detail_post.html', context=context)


@router.post('/{post_id}/')
async def post_detail(request: Request, post_id: int, post_service: PostService = Depends(), user=Depends(get_user)):
    if not user:
        return responses.RedirectResponse(f"/{post_id}/?msg=Вы не авторизованы", status_code=status.HTTP_302_FOUND)

    form = CommentCreateForm(request)
    await form.load_data()
    await post_service.create_comment(body=form.body, user_id=user.id, post_id=post_id)

    return responses.RedirectResponse(f"/{post_id}/?msg=Комментарий оставлен", status_code=status.HTTP_302_FOUND)


@router.get("/create_post")
def create_post(request: Request, user=Depends(get_user)):
    if not user or user.is_banned:
        return {'status': 'not logged or you are banned'}
    return templates.TemplateResponse("posts/create_post.html", {"request": request})


@router.post("/create_post")
async def create_post(request: Request, post_service: PostService = Depends(), user=Depends(get_user)):
    form = PostForm(request)
    await form.load_data()

    if not await form.is_valid():
        return templates.TemplateResponse("posts/create_post.html", form.__dict__)

    try:
        await post_service.create_post(data=form.data(), user_id=user.id)
        return responses.RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    except Exception as e:
        form.__dict__.get("errors").append(e)
        return templates.TemplateResponse("posts/create_post.html", form.__dict__)


@router.get('/update/{post_id}')
async def update_post(request: Request, post_id: int, post_service: PostService = Depends()):
    post = await post_service.get_post(post_id=post_id)
    form = PostForm(request).set_data(title=post.title, body=post.body)
    context = {
        'request': request,
        'form': form,
        'post': post
    }
    return templates.TemplateResponse('posts/update_post.html', context=context)


@router.post('/update_post/{post_id}')
async def update_post(request: Request, post_id: int, post_service: PostService = Depends()):
    form = PostForm(request)
    await form.load_data()

    if not await form.is_valid():
        return responses.RedirectResponse(f"/?msg={form.errors}", status_code=status.HTTP_302_FOUND)
    await post_service.update_post(post_id=post_id, form=form.data())

    return responses.RedirectResponse("/?msg=Изменения внесены успешно", status_code=status.HTTP_302_FOUND)


@router.post('/{post_id}/delete')
async def delete_post(request: Request, post_id: int, post_service: PostService = Depends()):
    await post_service.delete_post(post_id=post_id)
    return templates.TemplateResponse('posts/delete_post.html', {'request': request})


@router.post('/{comment_id}/delete_comment')
async def delete_comment(comment_id: int, post_service: PostService = Depends()):
    await post_service.delete_comment(comment_id=comment_id)
    return responses.RedirectResponse(f"/?msg=Комментарий удален", status_code=status.HTTP_302_FOUND)


@router.post('/{post_id}/like')
async def like_post(post_id: int, post_service: PostService = Depends(), user=Depends(get_user)):
    if not user:
        return responses.RedirectResponse("/?msg=Вы не авторизованы", status_code=status.HTTP_302_FOUND)
    msg = await post_service.like_post(post_id=post_id, user_id=user.id)
    return responses.RedirectResponse(f"/?msg={msg}", status_code=status.HTTP_302_FOUND)
