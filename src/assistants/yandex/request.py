import logging

from typing import Any
from aiohttp import ClientSession

logger = logging.getLogger(__name__)

class AliceRequest():
    def __init__(self, request_body: dict[str, Any], session: ClientSession) -> None:
        self.request_body = request_body
        self.session = session

    def __getitem__(self, key):
        return self.request_body[key]

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

        result = {}
        slots = self.request_body['request']['nlu']['intents'][intent]['slots']
        for slot in slots:
            result[slot] = slots[slot]['value']

        return result

    @property
    def original_utterance(self):
        return self.request_body.get('request', {}).get('original_utterance')
