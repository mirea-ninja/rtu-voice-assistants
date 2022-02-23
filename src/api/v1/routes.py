from fastapi import APIRouter

from .endpoints.voice import router as voice_router

router = APIRouter()
router.include_router(voice_router)
