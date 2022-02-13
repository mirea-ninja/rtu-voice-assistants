import logging
import collections

from typing import Awaitable

from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from starlette.status import HTTP_200_OK
from starlette.requests  import Request

from src.services.yandex import alice

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/alice",
    tags=["Alice"],
    status_code=HTTP_200_OK,
)
async def alice_webhook(request: Request,  service: Awaitable[alice.AliceVoiceAssistantService] = Depends(alice.get_alice_voice_assistant_service)) -> ORJSONResponse:

    if isinstance(service, collections.abc.Awaitable):
        service = await service
    logger.info(await request.json())
    response = await service.parse_request_and_routing(request=request)
    return ORJSONResponse(content=response)