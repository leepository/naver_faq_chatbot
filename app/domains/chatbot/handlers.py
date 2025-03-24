from app.domains.chatbot.repositories.chroma.chroma_chatbot_repository import ChromaChatbotRepository


class ChatbotHandler:

    def __init__(self, chatbot_repository: ChromaChatbotRepository):
        self.repository = chatbot_repository

    def retreive_documents(self, query: str, collection_name: str, n_results: int = 5):
        return self.repository.retrieve_documents(
            query=query,
            collection_name=collection_name,
            n_results=n_results
        )
