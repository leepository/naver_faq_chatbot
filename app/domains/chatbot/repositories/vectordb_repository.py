from abc import ABC, abstractmethod

class VectordbRepository(ABC):

    @abstractmethod
    def get_collection(self, collection_name):
        pass

    @abstractmethod
    def retrieve_documents(self, query: str, collection_name: str, n_result: int):
        pass
