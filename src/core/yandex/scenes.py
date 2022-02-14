import logging

from typing import Any, Awaitable, Callable, Optional
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, date

from src.core.config import SCHEDULE_API_URL
from src.core.yandex import intents
from src.core.yandex.state import STATE_REQUEST_KEY, STATE_RESPONSE_KEY
from src.assistants.yandex.request import AliceRequest
from src.crud.user import get_user

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

        if intents.HELP in request.intents or intents.WHAT_CAN_YOU_DO in request.intents:
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

        if len(text) > 1024:
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


class WelcomeDefault(BaseScene):

    async def reply(self, request: AliceRequest):
        text = 'Привет! Какое расписание тебе нужно сегодня?'
        return await self.make_response(text, tts=text)

    def handle_local_intents(self, request: AliceRequest):
        return self.handle_global_intents(request)

class Helper(BaseScene):

    async def reply(self, request: AliceRequest):
        text = "Я могу показать расписание твоей группы. Или, например, сказать количество пар сегодня"
        return await self.make_response(text, tts=text)

    def handle_local_intents(self, request: AliceRequest):
        return self.handle_global_intents(request)


class GroupManager(BaseScene):

    def __init__(self):

        self.intents_dict = {
            intents.USER_STUDY_GROUP_SET: self.user_group_set,
            intents.USER_STUDY_GROUP_UPDATE: self.user_group_update,
        }


    @property
    def intents_handler(self) -> dict[str, Callable[[AliceRequest], Awaitable]]:
        return self.intents_dict

    async def reply(self, request: AliceRequest) -> dict[str, Any]:
        intent = list(request.intents.keys())[0]
        handler = self.intents_handler[intent]
        return await handler(request)

    async def user_group_confirm(self, request: AliceRequest):
        pass

    async def user_group_reject(self, request: AliceRequest):
        pass

    async def user_group_set(self, request: AliceRequest):
        text = None
        return await self.make_response(text, tts=text)
    
    async def user_group_update(self, request: AliceRequest):
        text = None
        return await self.make_response(text, tts=text)

    def handle_local_intents(self, request: AliceRequest):
        if set(request.intents) & set(intents.USER_STUDY_GROUP_INTENTS):
            return self


class Schedule(BaseScene):
    def __init__(self):
        self.intents_dict = {
            intents.SCHEDULE_COUNT: self.schedule_info_count,
            intents.SCHEDULE_LIST: self.schedule_info_list,
        }

    @property
    def intents_handler(self) -> dict[str, Callable[[AliceRequest], Awaitable]]:
        return self.intents_dict

    async def reply(self, request: AliceRequest) -> dict[str, Any]:
        intent = list(request.intents.keys())[0]
        handler = self.intents_handler[intent]
        return await handler(request)

    async def __get_week_parity(self, day: date) -> int:
        # TODO: fix hardcode
        start_semestr_date = date(2022, 2, 7)
        end_semestr_date = date(2022, 6, 4)

        if day >= start_semestr_date and day <= end_semestr_date:
            return day.isocalendar().week - 5

    async def __get_day_num(self, day: str) -> str:

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

    async def __get_day_num_python(self, day: str) -> int:

        days = {
            "Monday": 0,
            "Tuesday": 1,
            "Wednesday": 2,
            "Thursday": 3,
            "Friday": 4,
            "Saturday": 5,
            "Sunday": 6,
        }

        return days[day]

    async def __get_day_name(self, day: str) -> str:

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

    async def __get_day_num_from_yandex(self, day: int) -> str:

        days = {
            0: f"{await self.__get_day_num(datetime.today().strftime('%A'))}",
            1: f"{await self.__get_day_num((datetime.today() + timedelta(days=1)).strftime('%A'))}"
        }

        return days[day]

    async def __convert_from_yandex_date(self, day: int) -> str:

        yandex_day_dict = {
            0: "Сегодня",
            1: "Завтра"
        }

        return yandex_day_dict[day]

    async def __convert_to_str(self, lessons_count: int) -> str:

        lesson_a = "пара"
        lesson_b = "пары"
        lesson_c = "пар"

        if lessons_count == 1:
            return lesson_a
        elif lessons_count >= 2 and lessons_count <= 4:
            return lesson_b
        elif lessons_count >= 5 or lessons_count == 0:
            return lesson_c

    async def __check_odd_array(self, array: list) -> bool:
        return len([n for n in array if n % 2]) > 0

    async def __get_schedule_count(self, schedule: dict, day: str, even: bool) -> int:
        count = 0

        for lesson in schedule['schedule'][day]['lessons']:
            if len(lesson) > 0:
                if len(lesson) == 1:
                    lesson_weeks_odd = await self.__check_odd_array(lesson[0]['weeks'])

                    if even and not lesson_weeks_odd:
                        count += 1
                    elif not even and lesson_weeks_odd:
                        count += 1

                elif len(lesson) >= 2:
                    count += 1

        return count

    async def __get_schedule_list(self, schedule: dict, group: str, day: str, date: str, even: bool) -> str:
        schedule_text = f"Расписание для группы {group} на {date}\n\n"

        for i in range(len(schedule['schedule'][day]['lessons'])):

            if len(schedule['schedule'][day]['lessons'][i]) > 0:

                if len(schedule['schedule'][day]['lessons'][i]) >= 2:
                    if even:
                        schedule_text += f"{i + 1}-ая пара. {schedule['schedule'][day]['lessons'][i][1]['name']}\n"
                    else:
                        schedule_text += f"{i + 1}-ая пара. {schedule['schedule'][day]['lessons'][i][0]['name']}\n"

                elif len(schedule['schedule'][day]['lessons'][i]) == 1:
                    lesson_weeks_odd = await self.__check_odd_array(schedule['schedule'][day]['lessons'][i][0]['weeks'])

                    if even and not lesson_weeks_odd:
                        schedule_text += f"{i + 1}-ая пара. {schedule['schedule'][day]['lessons'][i][0]['name']}\n"

        if schedule_text == f"Расписание для группы {group} на {date}\n\n":
            return "Пар нет! Отдыхайте!"

        return schedule_text

    async def __get_nearest_date(self, weekday) -> str:
        date_today = date.today()
        days_ahead = weekday - date_today.weekday()

        if days_ahead <= 0:
            days_ahead += 7

        return (date_today + timedelta(days_ahead)).strftime("%d.%m.%Y")

    async def schedule_info_count(self, request: AliceRequest):
        # TODO: REFACTOR

        day = request.slots.get('when', '')
        text = None

        yandex_datetime = False
        yandex_day = None

        py_date = None
        schedule_date = None

        parity = False

        if day == "YandexDatetime":
            entities = request.entities
            day = await self.__get_day_num_from_yandex(entities[0]['value']['day'])
            yandex_datetime = True
            yandex_day = await self.__convert_from_yandex_date(entities[0]['value']['day'])

        else:
            py_date = await self.__get_day_num_python(day)
            day = await self.__get_day_num(day)

        if day == "7":

            if yandex_datetime:

                if yandex_day == "Сегодня":
                    text = "Сегодня воскресенье, пар нет, можно отдыхать!"

                elif yandex_day == "Завтра":
                    text = "Завтра воскресенье, пар нет, можно отдыхать"

            else:
                text = "В воскресенье пар нет, можно отдыхать!"

        else:

            if yandex_datetime:

                if yandex_day == "Сегодня":
                    schedule_date = date.today().strftime("%d.%m.%Y")

                elif yandex_day == "Завтра":
                    schedule_date = (
                        date.today() + timedelta(days=1)).strftime("%d.%m.%Y")

            else:
                schedule_date = await self.__get_nearest_date(py_date)

            response_schedule_json = await self.get_request(request, group="ИКБО-30-20")

            week = await self.__get_week_parity(datetime.strptime(schedule_date, "%d.%m.%Y").date())

            if week % 2 == 0:
                parity = True

            lessons_count = await self.__get_schedule_count(response_schedule_json, day, parity)
            ru_ending = await self.__convert_to_str(lessons_count)

            if yandex_datetime:

                if yandex_day == "Сегодня":

                    if lessons_count == 0:
                        text = f"Сегодня у вас нет пар! Отдыхайте!"
                    else:
                        text = f"Сегодня у вас {lessons_count} {ru_ending}"

                elif yandex_day == "Завтра":

                    if lessons_count == 0:
                        text = f"Завтра у вас нет пар! Отдыхайте!"
                    else:
                        text = f"Завтра у вас {lessons_count} {ru_ending}"

            else:
                day = await self.__get_day_name(day)

                if lessons_count == 0:
                    if day == "Вторник":
                        text = f"Во {day.lower()} пар нет! Отдыхайте"
                    else:
                        text = f"В {day.lower()} пар нет! Отдыхайте"
                else:
                    if day == "Вторник":
                        text = f"Во {day.lower()} у вас {lessons_count} {ru_ending}"
                    else:
                        text = f"В {day.lower()} у вас {lessons_count} {ru_ending}"

        return await self.make_response(text, tts=text)

    async def schedule_info_list(self, request: AliceRequest):
        # TODO: REFACTOR

        day = request.slots.get('when', '')
        text = None

        yandex_datetime = False
        yandex_day = None

        py_date = None
        schedule_date = None

        parity = False

        if day == "YandexDatetime":
            entities = request.entities
            day = await self.__get_day_num_from_yandex(entities[0]['value']['day'])
            yandex_datetime = True
            yandex_day = await self.__convert_from_yandex_date(entities[0]['value']['day'])

        else:
            py_date = await self.__get_day_num_python(day)
            day = await self.__get_day_num(day)

        if day == "7":

            if yandex_datetime:

                if yandex_day == "Сегодня":
                    text = "Сегодня воскресенье, пар нет, можно отдыхать!"

                elif yandex_day == "Завтра":
                    text = "Завтра воскресенье, пар нет, можно отдыхать"

            else:
                text = "В воскресенье пар нет, можно отдыхать!"

        else:

            if yandex_datetime:

                if yandex_day == "Сегодня":
                    schedule_date = date.today().strftime("%d.%m.%Y")

                elif yandex_day == "Завтра":
                    schedule_date = (
                        date.today() + timedelta(days=1)).strftime("%d.%m.%Y")

            else:
                schedule_date = await self.__get_nearest_date(py_date)

            response_schedule_json = await self.get_request(request, group="ИКБО-30-20")

            week = await self.__get_week_parity(datetime.strptime(schedule_date, "%d.%m.%Y").date())

            if week % 2 == 0:
                parity = True

            text = await self.__get_schedule_list(response_schedule_json, "ИКБО-30-20", day, schedule_date, parity)

        return await self.make_response(text, tts=text)

    def handle_local_intents(self, request: AliceRequest):
        if set(request.intents) & set(intents.SCHEDULE_INTENTS):
            return self


SCENES = {
    "helper": Helper,
    "welcome": Welcome,
    "welcome_default": WelcomeDefault,
    "group": GroupManager,
    "schedule": Schedule
}
