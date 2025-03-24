from app.databases.internal import InternalState
from app.domains.chatbot.repositories.state_repository import StateRepository

class InternalStateRepository(StateRepository):

    def __init__(self, internal_state: InternalState):
        self.state = internal_state

    def add_state(self, state_data: dict):
        self.state.histories.append(state_data)

    def get_state(self):
        return self.state.histories

    def clear_state(self):
        self.state.histories = []
