from fastapi import APIRouter

from . import posts, auth

router = APIRouter()
router.include_router(posts.router)
router.include_router(auth.router)
