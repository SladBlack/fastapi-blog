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

from ..services.posts import ProductsService
from ..services.auth import get_current_user
from .forms import PostForm
from ..schemas import User

templates = Jinja2Templates(directory="src/blog/api/templates/")

router = APIRouter()


@router.get('/', response_class=HTMLResponse)
def get_posts(request: Request, products_service: ProductsService = Depends()):
    posts = products_service.get_posts()
    print('token', request.cookies.get('access_token'))
    return templates.TemplateResponse('posts/index.html', {'request': request, 'posts': posts})


@router.post('/{post_id}/delete')
def delete_post(request: Request, post_id: int, products_service: ProductsService = Depends()):
    products_service.delete_post(post_id=post_id)
    return templates.TemplateResponse('posts/delete_post.html', {'request': request})


@router.get("/create_post/")
def create_post(request: Request):
    # current_user: User = None
    # try:
    #     token = request.cookies.get("access_token")
    #     current_user: User = get_current_user(token=token)
    # except Exception as e:
    #     print(e)
    #     return 'Вы не авторизованы'
    return templates.TemplateResponse("posts/create_post.html", {"request": request})


@router.post("/create_post/")
async def create_post(request: Request, products_service: ProductsService = Depends()):
    form = PostForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            print('csrf: ', request.cookies.get('csrftoken'))
            token = request.cookies.get("access_token")
            print('token: ', token)
            scheme, param = get_authorization_scheme_param(token)
            current_user: User = get_current_user(token=token)
            form_data = form.data()
            products_service.create_post(form_data)
            form.__dict__.update(msg="Запись успешно добавилась")
            return responses.RedirectResponse("/", status_code=status.HTTP_302_FOUND)
        except Exception as e:
            print(e)
            form.__dict__.get("errors").append(
                "You might not be logged in, In case problem persists please contact us."
            )
            return templates.TemplateResponse("posts/create_post.html", form.__dict__)
    return templates.TemplateResponse("posts/create_post.html", form.__dict__, )


