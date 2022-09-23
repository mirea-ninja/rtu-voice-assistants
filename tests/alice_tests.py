import unittest
import sys
import random
import string

from fastapi_alice_tests import Interface, Skill
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.app import app
from src.database.database import Base, get_db
from src.database.migrate import migrate_test
from src.core.config import SKILL_ID

engine = create_engine("sqlite:///./tests/test.db",
                       connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
TestingSessionLocal = sessionmaker(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
migrate_test(TestingSessionLocal())


class TestYandexSkill(unittest.TestCase):
    skill = Skill(
        app, SKILL_ID, '/api/v1/alice')
    random_uid = "".join(random.choices(
        string.ascii_uppercase + string.ascii_lowercase + string.digits, k=10))

    def test_skill_response(self):
        self.assertTrue(TestYandexSkill.skill)

    def test_welcome_scene(self):
        session = TestYandexSkill.skill.new_session('TEST_NEW', [Interface.SCREEN])
        self.assertTrue(session.contain(
            "Привет! Теперь я умею показывать расписание РТУ МИРЭА. Для начала скажите мне свою группу."))

    def test_welcome_default_scene(self):
        session = TestYandexSkill.skill.new_session('TEST_DEFAULT', [Interface.SCREEN])
        self.assertTrue(session.contain(
            "Привет! Какое расписание вы хотите посмотреть?"))

    def test_help_scene(self):
        session = TestYandexSkill.skill.new_session(
            f'TEST_{TestYandexSkill.random_uid}', [Interface.SCREEN])
        session.send(
            "Помощь",
            command='помощь',
            nlu={
                "tokens": ["помощь"],
                "entities": [],
                "intents": {
                    "YANDEX.HELP": {
                        "slots": {}
                    }
                }
            }
        )
        self.assertTrue(session.contain(
            "Я могу показать расписание твоей группы. Или, например, сказать количество пар сегодня"))
        self.assertEqual(len(session.buttons), 5)

    def test_wcyd_scene(self):
        session = TestYandexSkill.skill.new_session(
            f'TEST_{TestYandexSkill.random_uid}', [Interface.SCREEN])
        session.send(
            "Что ты умеешь?",
            command='что ты умеешь',
            nlu={
                "tokens": ["что", "ты", "умеешь"],
                "entities": [],
                "intents": {
                    "YANDEX.WHAT_CAN_YOU_DO": {
                        "slots": {}
                    }
                }
            }
        )
        self.assertTrue(session.contain(
            "Я могу показать расписание твоей группы. Или, например, сказать количество пар сегодня"))
        self.assertEqual(len(session.buttons), 5)

    def test_groupmanager_scene(self):
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
