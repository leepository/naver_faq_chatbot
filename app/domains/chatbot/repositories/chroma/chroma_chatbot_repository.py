from app.databases.chroma import ChromaManager
from app.domains.chatbot.repositories.vectordb_repository import VectordbRepository

class ChromaChatbotRepository(VectordbRepository):

    def __init__(self, chromadb: ChromaManager):
        self.chromadb = chromadb
        self.client = self.chromadb.get_client()
        self.embedding_function = self.chromadb.get_embedding_function()

    def get_collection(self, collection_name: str):
        collection = self.client.get_collection(
            name=collection_name,
            embedding_function=self.embedding_function
        )
        return collection

    def retrieve_documents(self, query: str, collection_name: str, n_results: int):
        collection = self.get_collection(collection_name=collection_name)
        result = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return result
