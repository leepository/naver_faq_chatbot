from typing import List

from app.domains.chatbot.externals.llm_externals import LLMExternal
from app.llm.openai_async_manager import OpenAIAsyncManager

class OpenAIAsyncExternal(LLMExternal):

    def __init__(self, openai_async_manager: OpenAIAsyncManager):
        self.openai_client = openai_async_manager.get_client()
        self.openai_model = openai_async_manager.get_model()

    async def query(self, messages: List[dict]):
        response = await self.openai_client.chat.completions.create(
            model=self.openai_model,
            messages=messages,
            stream=True,
            max_tokens=1000,
            temperature=0.5
        )
        return response
