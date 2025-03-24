from abc import ABC, abstractmethod
from typing import List

class LLMExternal(ABC):

    @abstractmethod
    def query(self, messages: List[dict]):
        pass