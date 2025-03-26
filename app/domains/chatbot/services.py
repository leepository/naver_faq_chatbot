import asyncio
import ujson
from datetime import datetime

from app.domains.chatbot.handlers import (
    VectorDBHandler,
    StateHandler,
    LLMHandler,
    CacheHandler
)
from app.utils.common_utils import async_list_iterator

class ChatbotService:

    def __init__(
            self,
            cache_handler: CacheHandler,
            llm_handler: LLMHandler,
            state_handler: StateHandler,
            vectordb_handler: VectorDBHandler
    ):
        self.cache_handler = cache_handler
        self.llm_handler = llm_handler
        self.state_handler = state_handler
        self.vectordb_handler = vectordb_handler

        self.collection_name = 'naver_faq'
        self.cache_collection_name = 'query_cache'

    def make_answer(self, data):

        # Retrieve documents
        retrieved_docs = self.vectordb_handler.retrieve_documents(
            query=data.query,
            collection_name=self.collection_name,
            n_results=3
        )

        # Query LLM
        response = self.llm_handler.query_to_llm(
            query=data.query,
            context=retrieved_docs['documents'][0]
        )

        # Return result
        return response

    async def make_chat(self, request, data):

        # Check query cache
        caches = self.cache_handler.search_cache(
            query=data.query,
            collection_name=self.cache_collection_name
        )
        if caches is not None:
            cached_response = caches['metadatas'][0][0]['llm_response']
            id = caches['ids'][0]
            stream_response = [ujson.dumps({
                "id": id,
                "model": 'cache',
                "choices": [{
                    "delta": {
                        "role": None,
                        "content": d
                    },
                    "finish_reason": None,
                    "index": 0
                }]
            }) for d in str(cached_response)]
            stream_response.append(ujson.dumps({
                "id": id,
                "model": 'cache',
                "choices": [{
                    "delta": {
                        "role": None,
                        "content": ''
                    },
                    "finish_reason": 'stop',
                    "index": 0
                }]
            }))
            for chunk in stream_response:
                await asyncio.sleep(0.008)
                yield f"data: {chunk}\n\n"

        else:
            # Retrieve documents
            retrieved_docs = self.vectordb_handler.retrieve_documents(
                query=data.query,
                collection_name=self.collection_name,
                n_results=3
            )

            # Get chat histories
            chat_histories = self.state_handler.get_chat_histories()

            # Query LLM by stream
            stream = await self.llm_handler.query_to_llm_stream(query=data.query, context=retrieved_docs['documents'][0], histories=chat_histories)

            # prepare stream for client
            content = ""
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content += chunk.choices[0].delta.content
                if chunk.choices[0].finish_reason == 'stop':
                    chat_history = {
                        'user_query': data.query,
                        'llm_response': content,
                        'datetime': datetime.now()
                    }
                    # Chat history 저장
                    self.state_handler.set_chat_history(state_data=chat_history)
                    # User query caching
                    self.cache_handler.set_cache(collection_name=self.cache_collection_name, data=chat_history)

                if await request.is_disconnected():
                    break

                # SSE 형식으로 포멧팅
                chunk_data = ujson.dumps({
                    "id": chunk.id,
                    "model": chunk.model,
                    "choices": [{
                        "delta": {
                            "role": chunk.choices[0].delta.role if hasattr(chunk.choices[0].delta, "role") else None,
                            "content": chunk.choices[0].delta.content if hasattr(chunk.choices[0].delta, "content") else None
                        },
                        "finish_reason": chunk.choices[0].finish_reason,
                        "index": chunk.choices[0].index
                    }]
                })

                yield f"data: {chunk_data}\n\n"

    def clear_chat_histories(self):
        try:
            self.state_handler.clear_chat_histories()
            return True

        except Exception as ex:
            print(f'[EX] ChatbotService.clear_chat_histories : {ex}')
            return False

    def clear_cache(self):
        try:
            self.cache_handler.clear_cache(collection_name=self.cache_collection_name)
            return True

        except Exception as ex:
            print(f'[EX] ChatbotService.clear_cache : {ex}')
            return False