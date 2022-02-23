import logging
import collections

from typing import Awaitable

from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from starlette.status import HTTP_200_OK
from starlette.requests import Request

from ....services.yandex import alice
from ....services.vk import marusia
from ....services.sber import sber

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


@router.post(
    "/marusia",
    tags=["Marusia"],
    status_code=HTTP_200_OK,
)
async def marusia_webhook(request: Request,  service: Awaitable[marusia.MarusaVoiceAssistantService] = Depends(marusia.get_marusa_voice_assistant_service)) -> ORJSONResponse:

    if isinstance(service, collections.abc.Awaitable):
        service = await service
    logger.info(await request.json())
    response = await service.parse_request_and_routing(request=request)

    return ORJSONResponse(content=response)


@router.post(
    "/sber",
    tags=["Sber"],
    status_code=HTTP_200_OK,
)
async def sber_webhook(request: Request,  service: Awaitable[sber.SberVoiceAssistantService] = Depends(sber.get_sber_voice_assistant_service)) -> ORJSONResponse:

    if isinstance(service, collections.abc.Awaitable):
        service = await service
    logger.info(await request.json())
    response = await service.parse_request_and_routing(request=request)

    return ORJSONResponse(content=response)
