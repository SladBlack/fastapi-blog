from fastapi import (
    APIRouter,
    Depends,
    Request,
    HTTPException,
)
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from ..services.posts import ProductsService
from .forms import PostForm

templates = Jinja2Templates(directory="src/blog/api/templates/")

router = APIRouter()


@router.get('/', response_class=HTMLResponse)
def get_posts(request: Request, products_service: ProductsService = Depends()):
    posts = products_service.get_posts()
    return templates.TemplateResponse('posts/index.html', {'request': request, 'posts': posts})


@router.post('/{post_id}/delete')
def delete_post(request: Request, post_id: int, products_service: ProductsService = Depends()):
    products_service.delete_post(post_id=post_id)
    return templates.TemplateResponse('posts/delete_post.html', {'request': request})


@router.get("/create_post/")
def create_post(request: Request):
    return templates.TemplateResponse("posts/create_post.html", {"request": request})


@router.post("/create_post/")
async def create_post(request: Request, products_service: ProductsService = Depends()):
    form = PostForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            products_service.create_post(form.data())
            form.__dict__.update(msg="Запись успешно добавилась")
            return templates.TemplateResponse("posts/create_post.html", form.__dict__)
        except HTTPException:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append("Данные введены некорректно")
            return templates.TemplateResponse("posts/create_post.html", form.__dict__)
    return templates.TemplateResponse("posts/create_post.html", form.__dict__, )
