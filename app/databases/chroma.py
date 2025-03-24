import chromadb
import os

from chromadb.utils.embedding_functions.openai_embedding_function import OpenAIEmbeddingFunction
from dotenv import load_dotenv


class ChromaManager:

    def __init__(self):
        load_dotenv()
        openai_api_key = os.getenv('OPENAI_API_KEY')

        self.client = chromadb.PersistentClient('./chromadb')
        self.embedding_function = OpenAIEmbeddingFunction(
            api_key=openai_api_key,
            model_name='text-embedding-3-large'
        )

    def get_client(self):
        return self.client

    def get_embedding_function(self):
        return self.embedding_function
