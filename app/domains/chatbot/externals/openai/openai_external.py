from typing import List

from app.domains.chatbot.externals.llm_externals import LLMExternal
from app.llm.openai_manager import OpenAIManager

class OpenAIExternal(LLMExternal):

    def __init__(self, openai_manager: OpenAIManager):
        self.openai_client = openai_manager.get_client()
        self.openai_model = openai_manager.get_model()

    def query(self, messages: List[dict]):
        response = self.openai_client.chat.completions.create(
            model=self.openai_model,
            messages=messages
        )
        return response
