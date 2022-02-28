import collections
import logging

from aiohttp import ClientSession
from functools import lru_cache

from fastapi import Depends
from typing import Any, Awaitable
from starlette.requests import Request

from ...assistants.yandex.request import AliceRequest
from ...core.session import get_session
from ...core.yandex import intents 
from ...core.yandex.scenes import Welcome, SCENES, WelcomeDefault, Schedule
from ...core.yandex.state import STATE_REQUEST_KEY
from ...crud.user import create_user, get_user
from ...database.database import get_db, Session
from ...services.base.abc import VoiceAssistantServiceBase

logger = logging.getLogger(__name__)


class AliceVoiceAssistantService(VoiceAssistantServiceBase):
    def __init__(self, session: ClientSession, db: Session) -> None:
        self.session = session
        self.db = db

    async def parse_request_and_routing(self, request: Request) -> dict[str, Any]:

        event = await request.json()

        request = AliceRequest(request_body=event, session=self.session, db=self.db)
        current_scene_id = event.get('state', {}).get(
            STATE_REQUEST_KEY, {}).get('scene')

        if current_scene_id is None:

            if request.user_id != '':
                user_id = request.user_id
                user = await get_user(user_id, self.db)

                if user != None:
                    if request.new and (set(intents.SCHEDULE_INTENTS) & set(request.intents)):
                        return await Schedule().reply(request)
                    elif len(user.group) == 0:
                        return await Welcome().reply(request)
                    else:
                        return await WelcomeDefault().reply(request)
                else:

                    user = {
                        "user_id": user_id,
                        "group": "",
                        "platform": "YANDEX"
                    }

                    await create_user(user, self.db)
                    return await Welcome().reply(request)

            elif request.application_id != '':
                user_id = request.application_id
                user = await get_user(user_id, self.db)

                if user != None:
                    if request.new and (set(intents.SCHEDULE_INTENTS) & set(request.intents)):
                        return await Schedule().reply(request)
                    elif len(user.group) == 0:
                        return await Welcome().reply(request)
                    else:
                        return await WelcomeDefault().reply(request)
                else:
                    user = {
                        "user_id": user_id,
                        "group": "",
                        "platform": "YANDEX"
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
async def get_alice_voice_assistant_service(session: Awaitable[ClientSession] = Depends(get_session), db: Session = Depends(get_db)) -> AliceVoiceAssistantService:

    if isinstance(session, collections.abc.Awaitable):
        session = await session

    return AliceVoiceAssistantService(session=session, db=db)
