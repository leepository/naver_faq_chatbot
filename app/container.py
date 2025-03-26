from dependency_injector import containers, providers

from app.databases.chroma import ChromaManager
from app.databases.internal import InternalState
from app.domains.chatbot.externals.openai.openai_external import OpenAIExternal
from app.domains.chatbot.externals.openai.openai_async_external import OpenAIAsyncExternal
from app.domains.chatbot.handlers import (
    CacheHandler,
    LLMHandler,
    StateHandler,
    VectorDBHandler
)
from app.domains.chatbot.repositories.chroma.chroma_chatbot_repository import ChromaChatbotRepository
from app.domains.chatbot.repositories.internal_state.internal_state_repository import InternalStateRepository
from app.domains.chatbot.services import ChatbotService
from app.llm.openai_manager import OpenAIManager
from app.llm.openai_async_manager import OpenAIAsyncManager

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=[
        "app.domains.chatbot.apis"
    ])

    # LLM
    openai_model = 'gpt-4o'
    openai_manager = providers.Singleton(OpenAIManager, model=openai_model)
    openai_async_manager = providers.Singleton(OpenAIAsyncManager, model=openai_model)

    # DB
    chromadb_manager = providers.Singleton(ChromaManager)
    internal_state = providers.Singleton(InternalState)

    # Repositories
    chromadb_chatbot_repository = providers.Singleton(ChromaChatbotRepository, chromadb=chromadb_manager)
    internal_state_repository = providers.Singleton(InternalStateRepository, internal_state=internal_state)

    # External
    openai_external = providers.Singleton(OpenAIExternal, openai_manager=openai_manager)
    openai_async_external = providers.Singleton(OpenAIAsyncExternal, openai_async_manager=openai_async_manager)

    # Handlers
    cache_handler = providers.Singleton(CacheHandler, cache_repository=chromadb_chatbot_repository)
    llm_handler = providers.Singleton(LLMHandler, llm_external=openai_external, llm_async_external=openai_async_external)
    state_handler = providers.Singleton(StateHandler, state_repository=internal_state_repository)
    vectordb_handler = providers.Singleton(VectorDBHandler, chatbot_repository=chromadb_chatbot_repository)

    # services
    chatbot_service = providers.Singleton(
        ChatbotService,
        cache_handler=cache_handler,
        llm_handler=llm_handler,
        state_handler=state_handler,
        vectordb_handler=vectordb_handler
    )
