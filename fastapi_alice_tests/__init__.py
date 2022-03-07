"""
Helper for Yandex.Alice skill autotests
"""
from fastapi.testclient import TestClient


class Surface:
    """
    Available Alice surfaces
    """
    WINDOWS = 1
    MOBILE_AND_BROWSER = 2
    NAVIGATOR = 3
    STATION = 4


class Interface:
    """
    Available Alice interfaces
    """
    SCREEN = "screen"
    PAYMENTS = "payments"
    ACCOUNT_LINKING = "account_linking"
    AUDIO_PLAYER = "audio_player"


class Skill:
    """
    Approved Alice skill as fastapi app
    """
    sessions = {"current_id": 10000}

    def __init__(self, fastapi_app, skill_id, webhook_url, is_screen_need=False):
        self.app = fastapi_app
        self.client = TestClient(fastapi_app)
        self.skill_id = skill_id
        self.url = webhook_url
        self.is_screen_need = is_screen_need

    def new_session(
        self,
        user_id,
        interfaces,
        locale='ru-RU',
        timezone="Europe/Moscow",
        client_id="ru.yandex.searchplugin/5.80 (Samsung Galaxy; Android 4.4)",
        command=""
    ):
        """
        create new Alice session
        """
        return Session(self, user_id, interfaces, locale, timezone, client_id, command)


class Session:
    """
    Alice session
    """

    def __init__(self, skill, user_id, interfaces, locale, timezone, client_id, command=""):
        self.skill = skill
        self.messages = {}
        self.buttons = []

        self.version = "1.0"
        self.meta = {
            "locale": locale,
            "timezone": timezone,
            "client_id": client_id,
            "interfaces": {interface: {} for interface in interfaces}
        }
        self.state = {
            "session": {},
            "user": {},
            "application": {}
        }
        self.session = {
            "message_id": 0,
            "new": True,
            "session_id": "2eac4854-fce721f3-b845abba-{}".format(self.skill.sessions["current_id"]),
            "skill_id": self.skill.skill_id,
            "user": {
                "user_id": user_id
            },
            "application": {
                "application_id": user_id
            },

            "user_id": user_id
        }

        self.send(command, command=command)

        self.session["new"] = False
        self.skill.sessions["current_id"] += 1

    def send_button(self, index):
        """
        Alice user press button in the skill chat
        """
        button = self.buttons[index]
        req = {
            "nlu": {"entities": [], "tokens": []},
            "type": "SimpleUtterance",
            "original_utterance": button["title"],
        }

        if "payload" in button:
            req["payload"] = button["payload"]
            req["type"] = "ButtonPressed"

        self.send_request(req, "[{}]".format(button["title"]))

    def send(self, text, command="", nlu=None):
        """
        Alice user send text to skill
        """
        if not nlu:
            nlu = {"entities": [], "tokens": [], "intents": {}}

        req = {
            "command": command,
            "original_utterance": text,
            "nlu": nlu,
            "markup": {
                "dangerous_context": False
            },
            "type": "SimpleUtterance",

        }
        self.send_request(req, text)

    def send_request(self, req, text):
        """
        internal send function
        """
        data = {
            "meta": self.meta,
            "version": self.version,
            "session": self.session,
            "request": req,
            "state": self.state
        }

        response = self.skill.client.post(
            self.skill.url,
            json=data,
            headers={'content-type': 'application/json'}
        )

        assert response.status_code == 200
        response = response.json()

        if 'buttons' in response['response']:
            self.buttons = response['response']['buttons']
        else:
            self.buttons = [
                button for button in self.buttons if not button.get('hide', False)]

        for elem in response['session_state']:
            self.state['session'][elem] = response['session_state'][elem]

        self.messages[self.session["message_id"]] = (
            text, response['response']['text'])
        self.session["message_id"] += 1

    def clear(self):
        """
        Clear the chat history
        """
        self.messages = {}

    def dump(self, tail=5):
        """
        Print tail of the session history, order by message dates
        """
        suff = ''
        if len(self.messages) > tail:
            suff = 'Latest {}\n\n'.format(tail)

        lines = [suff]
        for message_id in sorted(self.messages)[-tail:]:
            req, res = self.messages[message_id]
            lines.append("Q: {}\nA: {}\n\n".format(req, res))

        if self.buttons:
            lines.append(
                '\n\n' + ' '.join(["[{}]".format(but["title"]) for but in self.buttons]))

        return ''.join(lines)

    def contain(self, substring, tail=5):
        """
        Check for presence of the substring in tail of chat history
        """
        for message_id in sorted(self.messages)[-tail:]:
            req, res = self.messages[message_id]
            if (substring in req) or (substring in res):
                return True

        return False
