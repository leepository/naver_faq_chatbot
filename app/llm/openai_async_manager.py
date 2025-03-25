from dotenv import load_dotenv
from openai import AsyncOpenAI

class OpenAIAsyncManager:

    def __init__(self, model: str):
        load_dotenv()
        self.async_client = AsyncOpenAI()
        self.model = model

    def get_client(self):
        return self.async_client

    def get_model(self):
        return self.model
