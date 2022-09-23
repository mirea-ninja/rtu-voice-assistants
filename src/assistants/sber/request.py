import logging

from typing import Any
from aiohttp import ClientSession

from ...database.database import Session
from ...core.yandex.state import STATE_REQUEST_KEY

logger = logging.getLogger(__name__)

class SberRequest():
    def __init__(self, request_body: dict[str, Any], session: ClientSession, db: Session) -> None:
        self.request_body = request_body
        self.session = session
        self.db = db

    def __getitem__(self, key):
        return self.request_body[key]
    
    @property
    def get_db(self):
        return self.db

    @property
    def user_id(self):
        return self.request_body['uuid'].get('userId', '')
    
    @property
    def sub(self):
        return self.request_body['uuid'].get('sub', '')

    @property
    def intents(self):
        return self.request_body['request'].get('nlu', {}).get('intents', {})

    @property
    def entities(self):
        return self.request_body['request'].get('nlu', {}).get('entities', {})

    @property
    def type(self):
        return self.request_body.get('request', {}).get('type')

    @property
    def slots(self):
        request_intents = self.request_body['request']['nlu']['intents']
        intent = list(request_intents.keys())[0]

        slots = self.request_body['request']['nlu']['intents'][intent]['slots']
        return {slot: slots[slot]['value'] for slot in slots}

    @property
    def original_text(self):
        return self.request_body.get('payload', {}).get('message', {}).get('original_text')
    
    @property
    def command(self):
        return self.request_body.get('request', {}).get('command')
    
    @property
    def get_group(self):
        return self.request_body.get('state', {}).get(STATE_REQUEST_KEY, {}).get('group')
    
    @property
    def intent(self):
        return self.request_body['payload'].get('intent', '')