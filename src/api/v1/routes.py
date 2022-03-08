from fastapi import APIRouter

from .endpoints.voice import router as voice_router
from .endpoints.uptime import router as uptime_router

router = APIRouter()
router.include_router(voice_router)
router.include_router(uptime_router)