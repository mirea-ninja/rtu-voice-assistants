import unittest
import sys
import random
import string

from fastapi_alice_tests import Interface, Skill
from src.app import app


class TestYandexSkill(unittest.TestCase):
    skill = Skill(
        app, 'd82b8851-a7c5-42bc-9907-4fea75f54f05', '/api/v1/alice')
    random_uid = "".join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=10))


    def test_skill_response(self):
        self.assertTrue(TestYandexSkill.skill)


    def test_new_welcome(self):
        session = TestYandexSkill.skill.new_session(
            f'TEST_NEW', [Interface.SCREEN])
        self.assertTrue(session.contain("Привет! Теперь я умею показывать расписание РТУ МИРЭА. Для начала скажите мне свою группу."))
                

    def test_default_welcome(self):
        session = TestYandexSkill.skill.new_session(
            f'TEST_DEFAULT', [Interface.SCREEN])
        self.assertTrue(session.contain("Привет! Какое расписание вы хотите посмотреть?"))


    def test_group(self):
        session = TestYandexSkill.skill.new_session(
            f'TEST_{TestYandexSkill.random_uid}', [Interface.SCREEN])
        session.send(
            "ИКБО-01-20",
            command='икбо - 01 - 20',
            nlu={
                "tokens": ["икбо", "01", "20"],
                "entities": [],
                "intents": {
                    "user_study_group_set": {
                        "slots": {
                            "group": {
                                "type": "YANDEX.STRING",
                                "tokens": {
                                    "start": 0,
                                    "end": 1
                                },
                                "value": "икбо"
                            }
                        }
                    }
                }
            }
        )
        self.assertTrue(session.contain("Ваша группа ИКБО-01-20, верно?"))
        self.assertEqual(len(session.buttons), 2)

        session.send(
            "Нет",
            command='нет',
            nlu={
                "tokens": ["нет"],
                "entities": [],
                "intents": {
                    "YANDEX.REJECT": {
                        "slots": {}
                    }
                }
            }
        )
        self.assertTrue(session.contain(
            "Давайте попробуем еще раз. Назовите вашу группу"))

        session.send(
            "ИКБО-01-20",
            command='икбо - 01 - 20',
            nlu={
                "tokens": ["икбо", "01", "20"],
                "entities": [],
                "intents": {
                    "user_study_group_set": {
                        "slots": {
                            "group": {
                                "type": "YANDEX.STRING",
                                "tokens": {
                                    "start": 0,
                                    "end": 1
                                },
                                "value": "икбо"
                            }
                        }
                    }
                }
            }
        )
        self.assertTrue(session.contain("Ваша группа ИКБО-01-20, верно?"))

        session.send(
            "Да",
            command='да',
            nlu={
                "tokens": ["да"],
                "entities": [],
                "intents": {
                    "YANDEX.CONFIRM": {
                        "slots": {}
                    }
                }
            }
        )

        self.assertTrue(session.contain(
            'Отлично, я запомнила, что вы из ИКБО-01-20. Для просмотра расписания скажите "Расписание на сегодня" или "Раписание на понедельник"\nДля просмотра помощи скажите "Помощь".\nЧтобы изменить группу скажите "Изменить группу'))
        self.assertEqual(len(session.buttons), 6)


sys.path.append(".")
