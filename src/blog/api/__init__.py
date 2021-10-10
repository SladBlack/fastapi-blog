from fastapi import APIRouter

from . import posts

router = APIRouter()
router.include_router(posts.router)
