import logging
import difflib
import re

from typing import Any, Awaitable, Callable, Optional
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, date

from ...assistants.vk.request import MarusiaRequest

from ...core.config import SCHEDULE_API_URL
from ...core.vk import intents
from ...core.vk.state import STATE_RESPONSE_KEY

from ...crud.user import get_user, update_user

from ...utils.schedule_utils import ScheduleUtils
from ...utils.response_utils import ReponseUtils

logger = logging.getLogger(__name__)


class BaseScene(ABC):

    @classmethod
    def id(cls):
        return cls.__name__

    @abstractmethod
    async def reply(self, request):
        ...

    def move(self, request: MarusiaRequest):
        next_scene = self.handle_local_intents(request)
        if next_scene is None:
            next_scene = self.handle_global_intents(request)
        return next_scene

    def handle_global_intents(self, request: MarusiaRequest):
        intents_set = set(request.intents)

        if intents.HELP in request.intents or intents.WHAT_CAN_YOU_DO in request.intents:
            return Helper()

        if intents_set & set(intents.SCHEDULE_INTENTS):
            return Schedule()

        if intents_set & set(intents.USER_STUDY_GROUP_INTENTS):
            return GroupManager()
        
        if intents_set & set(intents.EXIT_INTENTS):
            return GoodBye()

    async def handle_local_intents(self, request: MarusiaRequest) -> Optional[str]:
        ...

    async def fallback(self, request: MarusiaRequest):
        text = 'Не понимаю. Попробуйте сформулировать иначе. Скажите "Помощь" или "Что ты умеешь" и я помогу'

        logger.error(f'incomprehensible intent: {request.original_utterance}')

        return await self.make_response(text, tts=text)

    async def make_response(self, text, request: MarusiaRequest, tts=None, buttons=None, state=None, group=None, exit=False):

        if len(text) > 1024:
            text = text[:1024]

        if tts is None:
            tts = text.replace('\n', ', ')

        response = {
            'text': text,
            'tts': tts,
        }

        if buttons is not None:
            response['buttons'] = buttons

        if exit:
            response['end_session'] = True
        else:
            response['end_session'] = False

        derived_session_fields = ['session_id', 'user_id', 'message_id']

        webhook_response = {
            'response': response,
            'version': request['version'],
            "session": {derived_key: request['session'][derived_key] for derived_key in derived_session_fields},
            STATE_RESPONSE_KEY: {
                'scene': self.id(),
                'group': group
            },
        }
   
        if state is not None:
            webhook_response[STATE_RESPONSE_KEY].update(state)

        return webhook_response

    async def get_schedule_request(self, request: MarusiaRequest, group: str = 10):

        async with request.session.get(url=f"{SCHEDULE_API_URL}/{group}/full_schedule") as response:
            return await response.json()

    async def get_groups_request(self, request: MarusiaRequest):

        async with request.session.get(url=f"{SCHEDULE_API_URL}/groups") as response:
            return await response.json()


class Welcome(BaseScene):

    async def reply(self, request: MarusiaRequest):
        text = 'Привет! Теперь я умею показывать расписание РТУ МИРЭА. Для начала скажите мне свою группу.'
        return await self.make_response(text, tts=text, request=request)

    def handle_local_intents(self, request: MarusiaRequest):
        return self.handle_global_intents(request)


class WelcomeDefault(BaseScene):

    async def reply(self, request: MarusiaRequest):
        text = 'Привет! Какое расписание вы хотите посмотреть?'
        return await self.make_response(text, tts=text)

    def handle_local_intents(self, request: MarusiaRequest):
        return self.handle_global_intents(request)


class GoodBye(BaseScene):
    def __init__(self):

        self.intents_dict = {
            intents.EXIT: self.exit,
        }

    @property
    def intents_handler(self) -> dict[str, Callable[[MarusiaRequest], Awaitable]]:
        return self.intents_dict

    async def reply(self, request: MarusiaRequest) -> dict[str, Any]:
        intent = list(request.intents.keys())[0]
        handler = self.intents_handler[intent]
        return await handler(request)

    async def exit(self, request: MarusiaRequest):
        text = "До свидания, обращайтесь ко мне ещё!"
        return await self.make_response(text, tts=text, exit=True)

    def handle_local_intents(self, request: MarusiaRequest):
        if set(request.intents) & set(intents.USER_STUDY_GROUP_INTENTS):
            return self


class Helper(BaseScene):

    async def reply(self, request: MarusiaRequest):
        text = "Я могу показать расписание твоей группы. Или, например, сказать количество пар сегодня"
        return await self.make_response(text, tts=text, buttons=[
            ReponseUtils.button('Расписание на сегодня', hide=True),
            ReponseUtils.button('Расписание на завтра', hide=True),
            ReponseUtils.button('Сколько пар сегодня', hide=True),
            ReponseUtils.button('Расписание на понедельник', hide=True),
            ReponseUtils.button('Изменить группу', hide=True)
        ])

    def handle_local_intents(self, request: MarusiaRequest):
        return self.handle_global_intents(request)


class GroupManager(BaseScene):

    def __init__(self):

        self.intents_dict = {
            intents.USER_STUDY_GROUP_SET: self.user_group_set,
            intents.USER_STUDY_GROUP_UPDATE: self.user_group_update,
            intents.CONFIRM: self.user_group_confirm,
            intents.REJECT: self.user_group_reject
        }

    @property
    def intents_handler(self) -> dict[str, Callable[[MarusiaRequest], Awaitable]]:
        return self.intents_dict

    async def reply(self, request: MarusiaRequest) -> dict[str, Any]:
        intent = list(request.intents.keys())[0]
        handler = self.intents_handler[intent]
        return await handler(request)

    async def __find_user_group(self, groups: list, user_group: str):

        if len(user_group) < 5 or len(user_group) > 10:
            return None

        result = re.search(r'[а-яА-Яa-zA-Z]{5,}', user_group)

        if result:
            return None

        user_group = user_group.replace(' ', '')
        result = re.search(r'\d\d', user_group)

        if result:
            group_user_group = user_group[0:result.span()[0] - 1]
            group_number = result.group(0)

            for group in groups:
                group_temp = group[0:7]

                if group_user_group.lower() in group.lower() and group_number in group_temp:
                    year_number = user_group[result.span()[1]:]
                    year_number = re.findall(r'\d', year_number)

                    if len(year_number) > 0:
                        year_number = ''.join(year_number)
                        if len(year_number) == 2:
                            if group[8:] == year_number:
                                return group
                        elif len(year_number) == 1:
                            if group[8] == year_number:
                                return group
                    else:
                        return group

        else:
            list_matchers = [difflib.SequenceMatcher(
                None, user_group.lower(), group.lower()) for group in groups]
            list_matchers = [match.ratio() for match in list_matchers]
            return groups[list_matchers.index(max(list_matchers))]

    async def user_group_confirm(self, request: MarusiaRequest):
        user_group = request.get_group

        if request.user_id != '':
            user_id = request.user_id
            user = {
                "user_id": user_id,
                "group": user_group
            }

            await update_user(user, request.db)

        elif request.application_id != '':
            user_id = request.application_id
            user = {
                "user_id": user_id,
                "group": user_group
            }

            await update_user(user, request.db)

        text = f'Отлично, я запомнила, что вы из {user_group}. Для просмотра расписания скажите "Расписание на сегодня" или "Расписание на понедельник"\nДля просмотра помощи скажите "Помощь".\nЧтобы изменить группу скажите "Изменить группу"'
        return await self.make_response(text, tts=text, buttons=[
            ReponseUtils.button('Расписание на сегодня', hide=True),
            ReponseUtils.button('Расписание на завтра', hide=True),
            ReponseUtils.button('Сколько пар сегодня', hide=True),
            ReponseUtils.button('Помощь', hide=True),
            ReponseUtils.button('Что ты умеешь?', hide=True),
            ReponseUtils.button('Изменить группу', hide=True),
        ])

    async def user_group_reject(self, request: MarusiaRequest):
        self.user_group = ""
        text = f"Давайте попробуем еще раз. Назовите вашу группу"
        return await self.make_response(text, tts=text)

    async def user_group_set(self, request: MarusiaRequest):
        groups_json = await self.get_groups_request(request)
        group = request.command
        user_group = await self.__find_user_group(groups_json['groups'],  group)
        text = f"Ваша группа {user_group}, верно?"

        return await self.make_response(text, tts=text, group=user_group, buttons=[
            ReponseUtils.button('Да', hide=True),
            ReponseUtils.button('Нет', hide=True)
        ])

    async def user_group_update(self, request: MarusiaRequest):
        text = "Хорошо, назовите новую группу и я её запомню"
        return await self.make_response(text, tts=text)

    def handle_local_intents(self, request: MarusiaRequest):
        if set(request.intents) & set(intents.USER_STUDY_GROUP_INTENTS):
            return self


class Schedule(BaseScene):
    def __init__(self):
        self.intents_dict = {
            intents.SCHEDULE_COUNT: self.schedule_info_count,
            intents.SCHEDULE_LIST: self.schedule_info_list,
        }

    @property
    def intents_handler(self) -> dict[str, Callable[[MarusiaRequest], Awaitable]]:
        return self.intents_dict

    async def reply(self, request: MarusiaRequest) -> dict[str, Any]:
        intent = list(request.intents.keys())[0]
        handler = self.intents_handler[intent]
        return await handler(request)

    async def __get_week_parity(self, day: datetime) -> bool:
        return ScheduleUtils.get_week(day) % 2

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

        lesson_type = {
            "лк": "Лекция",
            "пр": "Практика"
        }

        for i in range(len(schedule['schedule'][day]['lessons'])):

            if len(schedule['schedule'][day]['lessons'][i]) > 0:

                if len(schedule['schedule'][day]['lessons'][i]) >= 2:
                    if even:
                        schedule_text += f"{i + 1}-ая пара. {schedule['schedule'][day]['lessons'][i][1]['name']}. {lesson_type[schedule['schedule'][day]['lessons'][i][1]['types']]}.\n"
                    else:
                        schedule_text += f"{i + 1}-ая пара. {schedule['schedule'][day]['lessons'][i][0]['name']}. {lesson_type[schedule['schedule'][day]['lessons'][i][0]['types']]}.\n"

                elif len(schedule['schedule'][day]['lessons'][i]) == 1:
                    lesson_weeks_odd = await self.__check_odd_array(schedule['schedule'][day]['lessons'][i][0]['weeks'])

                    if even and not lesson_weeks_odd:
                        schedule_text += f"{i + 1}-ая пара. {schedule['schedule'][day]['lessons'][i][0]['name']}. {lesson_type[schedule['schedule'][day]['lessons'][i][0]['types']]}.\n"

        if schedule_text == f"Расписание для группы {group} на {date}\n\n":
            return "Пар нет! Отдыхайте!"

        return schedule_text

    async def __get_nearest_date(self, weekday) -> str:
        date_today = date.today()
        days_ahead = weekday - date_today.weekday()

        if days_ahead <= 0:
            days_ahead += 7

        return (date_today + timedelta(days_ahead)).strftime("%d.%m.%Y")

    async def schedule_info_count(self, request: MarusiaRequest):
        # TODO: REFACTOR

        day = request.slots.get('when', '')
        text = None
        group = None

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

            if request.user_id != '':
                user_id = request.user_id
                user = await get_user(user_id, request.get_db)

            elif request.application_id != '':
                user_id = request.application_id
                user = await get_user(user_id, request.get_db)

            response_schedule_json = await self.get_schedule_request(request, group=user.group)
            parity = await self.__get_week_parity(datetime.strptime(schedule_date, "%d.%m.%Y"))

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

    async def schedule_info_list(self, request: MarusiaRequest):
        # TODO: REFACTOR

        day = request.slots.get('when', '')
        text = None
        group = None

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

            if request.user_id != '':
                user_id = request.user_id
                user = await get_user(user_id, request.get_db)

            elif request.application_id != '':
                user_id = request.application_id
                user = await get_user(user_id, request.get_db)

            response_schedule_json = await self.get_schedule_request(request, group=user.group)
            parity = await self.__get_week_parity(datetime.strptime(schedule_date, "%d.%m.%Y"))

            text = await self.__get_schedule_list(response_schedule_json, user.group, day, schedule_date, parity)

        return await self.make_response(text, tts=text)

    def handle_local_intents(self, request: MarusiaRequest):
        if set(request.intents) & set(intents.SCHEDULE_INTENTS):
            return self


SCENES = {
    "helper": Helper,
    "welcome": Welcome,
    "welcome_default": WelcomeDefault,
    "exit": GoodBye,
    "group": GroupManager,
    "schedule": Schedule
}
