import collections
import logging

from abc import ABC, abstractmethod
from aiohttp import ClientSession
from functools import lru_cache

from fastapi import Depends
from typing import Union, Any, Awaitable
from starlette.requests import Request

from ...core.session import get_session
from ...assistants.sber.request import SberRequest
from ...core.sber.scenes import Welcome, SCENES, WelcomeDefault
from ...core.sber.state import STATE_REQUEST_KEY
from ...crud.user import create_user, get_user
from ...database.database import get_db, Session

logger = logging.getLogger(__name__)


class VoiceAssistantServiceBase(ABC):

    @abstractmethod
    def parse_request_and_routing(self, *args, **kwargs) -> Union[Any, Awaitable[Any]]:
        ...


class SberVoiceAssistantService(VoiceAssistantServiceBase):
    def __init__(self, session: ClientSession, db: Session) -> None:
        self.session = session
        self.db = db

    async def parse_request_and_routing(self, request: Request) -> dict[str, Any]:

        event = await request.json()

        request = SberRequest(request_body=event, session=self.session, db=self.db)
        current_scene_id = event.get('payload', {}).get('intent')

        if current_scene_id is None or current_scene_id == "run_app":

            if request.sub != '':
                user_id = request.sub

                if await get_user(user_id, self.db) != None:
                    return await WelcomeDefault().reply(request)
                user = {
                    "user_id": user_id, 
                    "group": "",
                    "platform": "SBER"
                }

                await create_user(user, self.db)
                return await Welcome().reply(request)

            elif request.user_id != '':
                user_id = request.user_id

                if await get_user(user_id, self.db) != None:
                    return await WelcomeDefault().reply(request)
                user = {
                    "user_id": user_id,
                    "group": "",
                    "platform": "SBER"
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
async def get_sber_voice_assistant_service(session: Awaitable[ClientSession] = Depends(get_session), db: Session = Depends(get_db)) -> SberVoiceAssistantService:

    if isinstance(session, collections.abc.Awaitable):
        session = await session

    return SberVoiceAssistantService(session=session, db=db)
