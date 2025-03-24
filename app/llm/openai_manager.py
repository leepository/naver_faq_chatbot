from dotenv import load_dotenv
from openai import OpenAI

class OpenAIManager:

    def __init__(self, model: str):
        load_dotenv()
        self.openai_client = OpenAI()
        self.openai_model = model

    def get_client(self):
        return self.openai_client

    def get_model(self):
        return self.openai_model
