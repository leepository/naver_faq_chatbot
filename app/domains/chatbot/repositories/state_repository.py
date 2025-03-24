from abc import ABC, abstractmethod

class StateRepository(ABC):

    @abstractmethod
    def add_state(self, state_data: dict):
        pass

    @abstractmethod
    def get_state(self):
        pass

    @abstractmethod
    def clear_state(self):
        pass