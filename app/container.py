from dependency_injector import containers, providers

from app.databases.chroma import ChromaManager
from app.domains.chatbot.handlers import ChatbotHandler
from app.domains.chatbot.repositories.chroma.chroma_chatbot_repository import ChromaChatbotRepository
from app.domains.chatbot.services import ChatbotService

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=[
        "app.domains.chatbot.apis"
    ])

    # DB
    chromadb_manager = providers.Singleton(ChromaManager)

    # Repositories
    chromadb_chatbot_repository = providers.Singleton(ChromaChatbotRepository, chromadb=chromadb_manager)

    # Handlers
    chatbot_handler = providers.Singleton(ChatbotHandler, chatbot_repository=chromadb_chatbot_repository)

    # services
    chatbot_service = providers.Singleton(ChatbotService, chatbot_handler=chatbot_handler)
