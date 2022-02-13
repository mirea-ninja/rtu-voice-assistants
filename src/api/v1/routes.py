from fastapi import APIRouter

from src.api.v1.endpoints.voice import router as voice_router

router = APIRouter()
router.include_router(voice_router)
