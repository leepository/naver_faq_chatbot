from app.databases.chroma import ChromaManager
from app.domains.chatbot.repositories.vectordb_repository import VectordbRepository
from app.domains.chatbot.repositories.cache_repository import CacheRepository
from app.utils.common_utils import get_uuid

class ChromaChatbotRepository(VectordbRepository, CacheRepository):

    def __init__(self, chromadb: ChromaManager):
        self.chromadb = chromadb
        self.client = self.chromadb.get_client()
        self.embedding_function = self.chromadb.get_embedding_function()

    def get_collection(self, collection_name: str):
        collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"}
        )
        return collection


    def retrieve_documents(self, query: str, collection_name: str, n_results: int):
        collection = self.get_collection(collection_name=collection_name)
        result = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return result

    def add_cache(self, collection_name: str, user_query: str, metadata: dict):
        collection = self.get_collection(collection_name=collection_name)
        doc_id = get_uuid()
        collection.add(
            ids=[doc_id],
            documents=[user_query],
            metadatas=[metadata]
        )

    def search_cache(self, collection_name: str, query: str):
        collection = self.get_collection(collection_name=collection_name)
        doc = collection.query(
            query_texts=[query],
            n_results=1,
            include=['documents', 'metadatas', 'distances']
        )
        if len(doc['distances'][0]) > 0 and doc['distances'][0][0] < 0.2:
            return doc
        return None

    def clear_cache(self, collection_name: str):
        collection = self.get_collection(collection_name=collection_name)
        ids = collection.get()['ids']
        collection.delete(ids=ids)
