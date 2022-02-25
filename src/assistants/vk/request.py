import logging

from typing import Any
from aiohttp import ClientSession

from ...database.database import Session
from ...core.yandex.state import STATE_REQUEST_KEY

logger = logging.getLogger(__name__)

class MarusiaRequest():
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
        return self.request_body.get('user', {}).get('user_id', '')
    
    @property
    def application_id(self):
        return self.request_body.get('session', {}).get('application', {}).get('application_id', '')

    @property
    def entities(self):
        return self.request_body['request'].get('nlu', {}).get('entities', {})

    @property
    def type(self):
        return self.request_body.get('request', {}).get('type')

    @property
    def original_utterance(self):
        return self.request_body.get('request', {}).get('original_utterance')
    
    @property
    def command(self):
        return self.request_body.get('request', {}).get('command')
    
    @property
    def get_group(self):
        return self.request_body.get('state', {}).get(STATE_REQUEST_KEY, {}).get('group')
