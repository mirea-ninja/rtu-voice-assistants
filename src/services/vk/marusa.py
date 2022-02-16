import collections
import logging
from functools import lru_cache
from typing import Any, Awaitable

from aiohttp import ClientSession
from src.core.session import get_session
from fastapi import Depends
from starlette.requests import Request

from src.assistants.yandex.request import AliceRequest
from src.core.yandex.scenes import Welcome, SCENES
from src.core.yandex.state import STATE_REQUEST_KEY

logger = logging.getLogger(__name__)


class MarusaVoiceAssistantService():
    def __init__(self, session: ClientSession) -> None:
        self.session = session

    async def parse_request_and_routing(self, request: Request) -> dict[str, Any]:

        event = await request.json()

        request = AliceRequest(request_body=event, session=self.session)
        current_scene_id = event.get('state', {}).get(STATE_REQUEST_KEY, {}).get('scene')

        if current_scene_id is None:
            return await Welcome().reply(request)

        current_scene = SCENES.get(current_scene_id, Welcome())()
        next_scene = current_scene.move(request)

        if next_scene is not None:
            return await next_scene.reply(request)
        else:
            return await current_scene.fallback(request)


@lru_cache()
async def get_alice_voice_assistant_service(session: Awaitable[ClientSession] = Depends(get_session)) -> MarusaVoiceAssistantService:

    if isinstance(session, collections.abc.Awaitable):
        session = await session

    return MarusaVoiceAssistantService(session=session)