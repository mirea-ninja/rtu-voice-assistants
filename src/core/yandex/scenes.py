from email.headerregistry import Group
import logging

from typing import Any, Awaitable, Callable, Optional
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from src.core.config import SCHEDULE_API_URL
from src.core.yandex import intents
from src.core.yandex.state import STATE_REQUEST_KEY, STATE_RESPONSE_KEY
from src.assistants.yandex.request import AliceRequest

logger = logging.getLogger(__name__)


class BaseScene(ABC):

    @classmethod
    def id(cls):
        return cls.__name__

    @abstractmethod
    async def reply(self, request):
        ...

    def move(self, request: AliceRequest):
        next_scene = self.handle_local_intents(request)
        if next_scene is None:
            next_scene = self.handle_global_intents(request)
        return next_scene

    def handle_global_intents(self, request: AliceRequest):
        intents_set = set(request.intents)

        if intents.HELP in request.intents:
            return Helper()

        if intents_set & set(intents.SCHEDULE_INTENTS):
            return Schedule()

    async def handle_local_intents(self, request: AliceRequest) -> Optional[str]:
        ...

    async def fallback(self, request: AliceRequest):
        text = 'Не понимаю. Попробуй сформулировать иначе'

        logger.error(f'incomprehensible intent: {request.original_utterance}')

        return await self.make_response(text, tts=text)

    async def make_response(self, text, tts=None, state=None):

        if not text:
            text = ('К сожалению, по твоему запросу ничего не нашлось. '
                    'Попробуй спросить что-нибудь еще!')

        elif len(text) > 1024:
            text = text[:1024]

        if tts is None:
            tts = text.replace('\n', ', ')

        response = {
            'text': text,
            'tts': tts,
        }

        webhook_response = {
            'response': response,
            'version': '1.0',
            STATE_RESPONSE_KEY: {
                'scene': self.id(),
            },
        }
        if state is not None:
            webhook_response[STATE_RESPONSE_KEY].update(state)

        return webhook_response

    async def get_request(self, request: AliceRequest, group: str = 10):

        async with request.session.get(url=f"{SCHEDULE_API_URL}/{group}/full_schedule") as response:
            return await response.json()


class Welcome(BaseScene):

    async def reply(self, request: AliceRequest):
        text = 'Привет! Теперь я умею показывать расписание РТУ МИРЭА. Для начала скажи мне свою группу.'
        return await self.make_response(text, tts=text)

    def handle_local_intents(self, request: AliceRequest):
        return self.handle_global_intents(request)


class Helper(BaseScene):

    async def reply(self, request):

        text = "Я могу показать расписание твоей группы. Или, например, сказать количество пар сегодня"

        return await self.make_response(text, tts=text)

    def handle_local_intents(self, request: AliceRequest):
        pass


class Schedule(BaseScene):
    def __init__(self):
        self.intents_dict = {
            intents.SCHEDULE_COUNT: self.schedule_info_count,
            # intents.SCHEDULE_LIST: self.schedule_info_list,
        }
        self.user_group = None

    @property
    def intents_handler(self) -> dict[str, Callable[[AliceRequest], Awaitable]]:
        return self.intents_dict

    async def reply(self, request: AliceRequest) -> dict[str, Any]:
        intent = list(request.intents.keys())[0]
        handler = self.intents_handler[intent]
        return await handler(request)

    async def __get_week_num(self):
        pass

    async def __get_day_num(self, day: str):
        
        days = {
            "Monday": "1",
            "Tuesday": "2",
            "Wednesday": "3",
            "Thursday": "4",
            "Friday": "5",
            "Saturday": "6",
            "Sunday": "7",
        }

        return days[day]
    
    async def __get_day_name(self, day: str):

        days = {
            "1": "Понедельник",
            "2": "Вторник",
            "3": "Среду",
            "4": "Четверг",
            "5": "Пятницу",
            "6": "Субботу",
            "7": "Воскресенье",
        }

        return days[day]

    async def __get_day_num_from_yandex(self, day: int):
        
        days = {
            0: f"{await self.__get_day_num(datetime.today().strftime('%A'))}",
            1: f"{await self.__get_day_num((datetime.today() + timedelta(days=1)).strftime('%A'))}"
        }

        return days[day]


    async def __get_schedule_count(self, schedule: dict, day: str, even: bool = True):
        count = 0

        for lesson in schedule['schedule'][day]['lessons']:
            if len(lesson) > 0:
                if len(lesson) == 1:
                    if even:
                        if self.__check_even_array(lesson[0]['weeks']):
                            count += 1

                elif len(lesson) == 2 or len(lesson) == 4:
                    count += 1

        return count 

    async def __check_even_array(self, array: list):

        return len([n for n in array if n%2]) > 0

    async def schedule_info_count(self, request: AliceRequest):
        
        day = request.slots.get('when', '')
        text = None

        yandex_datetime = False
        yandex_day_dict = {
            0: "Сегодня",
            1: "Завтра"
        }
        yandex_day = None
           
        if day == "YandexDatetime":
            entities = request.entities
            day = await self.__get_day_num_from_yandex(entities[0]['value']['day'])
            yandex_datetime = True
            yandex_day = yandex_day_dict[entities[0]['value']['day']]

        else:
            day = await self.__get_day_num(day)
        
        if day == "7":

            if yandex_datetime:

                if yandex_day == "Сегодня":
                    text = "Сегодня, воскресенье пар нет, можно отдыхать"

                elif yandex_day == "Завтра":
                    text = "Завтра воскресенье, пар нет, можно отдыхать"

            else:
                text = "В воскресенье пар нет, можно отдыхать"

        else:   
            response_schedule_json = await self.get_request(request, group = "ИКБО-30-20")
            lessons_count = await self.__get_schedule_count(response_schedule_json, day, True)

            if yandex_datetime:

                if yandex_day == "Сегодня":
                    text = f"Сегодня у тебя {lessons_count} пар"

                elif yandex_day == "Завтра":
                    text = f"Завтра у тебя {lessons_count} пар"

            else:
                text = f"В {await self.__get_day_name(day)} у тебя {lessons_count} пар"
        
        return await self.make_response(text, tts=text)

    async def schedule_info_list(self, request: AliceRequest):
        raise NotImplementedError

    def handle_local_intents(self, request: AliceRequest):
        if set(request.intents) & set(intents.SCHEDULE_INTENTS):
            return self

class Group(BaseScene):
    def __init__(self):
        self.intents_dict = {
            intents.USER_STUDY_GROUP: self.set_user_group,
        }

    @property
    def intents_handler(self) -> dict[str, Callable[[AliceRequest], Awaitable]]:
        return self.intents_dict

    async def reply(self, request: AliceRequest) -> dict[str, Any]:
        intent = list(request.intents.keys())[0]
        handler = self.intents_handler[intent]
        return await handler(request)

    async def set_user_group(self, request: AliceRequest):

        group = request.slots.get('user_group_name', '')

        text = f"Отлично, теперь я знаю, что ты из {group}"

        return await self.make_response(text)


    def handle_local_intents(self, request: AliceRequest):
        if set(request.intents) & set(intents.SCHEDULE_INTENTS):
            return self

SCENES = {
    "helper": Helper,
    "welcome": Welcome,
    "group": Group,
    "schedule": Schedule
}
