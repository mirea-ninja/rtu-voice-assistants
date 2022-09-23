import collections
import logging

from aiohttp import ClientSession
from functools import lru_cache
from typing import Any, Awaitable

from fastapi import Depends
from starlette.requests import Request

from ...assistants.vk.request import MarusiaRequest
from ...core.session import get_session
from ...core.vk import intents 
from ...core.vk.scenes import Schedule, Welcome, WelcomeDefault, SCENES
from ...core.vk.state import STATE_REQUEST_KEY
from ...crud.user import create_user, get_user
from ...database.database import get_db, Session
from ...services.base.abc import VoiceAssistantServiceBase

logger = logging.getLogger(__name__)


class MarusaVoiceAssistantService(VoiceAssistantServiceBase):
    def __init__(self, session: ClientSession, db: Session) -> None:
        self.session = session
        self.db = db

    async def parse_request_and_routing(self, request: Request) -> dict[str, Any]:

        event = await request.json()

        request = MarusiaRequest(request_body=event, session=self.session, db=self.db)
        current_scene_id = event.get('state', {}).get(
            STATE_REQUEST_KEY, {}).get('scene')
        logger.info(current_scene_id)

        if current_scene_id is None:
            if request.user_id != '':
                user_id = request.user_id

                if await get_user(user_id, self.db) != None:
                    return await WelcomeDefault().reply(request)
                user = {
                    "user_id": user_id,
                    "group": "",
                    "platform": "VK"
                }

                await create_user(user, self.db)
                return await Welcome().reply(request)

            elif request.application_id != '':
                user_id = request.application_id

                if await get_user(user_id, self.db) != None:
                    return await WelcomeDefault().reply(request)
                user = {
                    "user_id": user_id,
                    "group": "",
                    "platform": "VK"
                }

                await create_user(user, self.db)
                return await Welcome().reply(request)

        current_scene = SCENES.get(current_scene_id, Welcome)()
        next_scene = current_scene.move(request)

        if next_scene is not None:
            return await next_scene.reply(request)
        else:
            return await current_scene.fallback(request)


@lru_cache()
async def get_marusa_voice_assistant_service(session: Awaitable[ClientSession] = Depends(get_session), db: Session = Depends(get_db)) -> MarusaVoiceAssistantService:

    if isinstance(session, collections.abc.Awaitable):
        session = await session

    return MarusaVoiceAssistantService(session=session, db=db)