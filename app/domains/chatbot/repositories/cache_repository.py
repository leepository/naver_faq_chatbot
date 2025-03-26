from abc import ABC, abstractmethod
from typing import List

class CacheRepository(ABC):

    @abstractmethod
    def add_cache(self, collection_name: str, user_query: str, metadata: dict):
        pass

    @abstractmethod
    def search_cache(self, collection_name: str, query: str):
        pass

    @abstractmethod
    def clear_cache(self, collection_name: str):
        pass