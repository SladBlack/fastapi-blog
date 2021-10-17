from fastapi import APIRouter

from . import posts, auth, profile

router = APIRouter()
router.include_router(posts.router)
router.include_router(auth.router)
router.include_router(profile.router)
