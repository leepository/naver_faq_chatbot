from dependency_injector import containers, providers

from app.databases.chroma import ChromaManager
from app.domains.chatbot.externals.openai.openai_external import OpenAIExternal
from app.domains.chatbot.handlers import ChatbotHandler
from app.domains.chatbot.repositories.chroma.chroma_chatbot_repository import ChromaChatbotRepository
from app.domains.chatbot.services import ChatbotService
from app.llm.openai_manager import OpenAIManager

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=[
        "app.domains.chatbot.apis"
    ])

    # LLM
    openai_model = 'gpt-4o'
    openai_manager = providers.Singleton(OpenAIManager, model=openai_model)

    # DB
    chromadb_manager = providers.Singleton(ChromaManager)

    # Repositories
    chromadb_chatbot_repository = providers.Singleton(ChromaChatbotRepository, chromadb=chromadb_manager)

    # External
    openai_external = providers.Singleton(OpenAIExternal, openai_manager=openai_manager)

    # Handlers
    chatbot_handler = providers.Singleton(ChatbotHandler, chatbot_repository=chromadb_chatbot_repository, openai_external=openai_external)

    # services
    chatbot_service = providers.Singleton(ChatbotService, chatbot_handler=chatbot_handler)
