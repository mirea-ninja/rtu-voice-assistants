from abc import ABC, abstractmethod
from typing import Union, Any, Awaitable

class VoiceAssistantServiceBase(ABC):

    @abstractmethod
    def parse_request_and_routing(self, *args, **kwargs) -> Union[Any, Awaitable[Any]]:
        ...