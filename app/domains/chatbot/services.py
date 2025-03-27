import asyncio
import ujson
from datetime import datetime

from app.common.exceptions import APIException, exception_handler
from app.domains.chatbot.handlers import (
    VectorDBHandler,
    StateHandler,
    LLMHandler,
    CacheHandler
)
from app.domains.chatbot.exceptions import LLMLengthOverError
from app.utils.log_utils import api_logger

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
        """
        JSON 방식의 응답
        :param data:
        :return:
        """
        # Check query cache
        caches = self.cache_handler.search_cache(
            query=data.query,
            collection_name=self.cache_collection_name
        )

        if caches is not None:
            cached_response = caches['metadatas'][0][0]

            chat_history = {
                'user_query': data.query,
                'llm_response': cached_response['llm_response'],
                'questions': cached_response['questions'],
                'datetime': datetime.now()
            }
            # Chat history 저장
            self.state_handler.set_chat_history(state_data=chat_history)

            return {
                "answer": cached_response['llm_response'],
                "questions": cached_response['questions'].split("|") if 'questions' in cached_response else None
            }
        else:
            # Retrieve documents
            retrieved_docs = self.vectordb_handler.retrieve_documents(
                query=data.query,
                collection_name=self.collection_name,
                n_results=3
            )

            # Get chat histories
            chat_histories = self.state_handler.get_chat_histories()

            # Reform user query
            reform_result = self.llm_handler.query_to_reform(query=data.query, histories=chat_histories)
            reform_json = ujson.loads(reform_result)
            reformed_query = reform_json['user_question'] if 'user_question' in reform_json and reform_json is not None else None

            # Query LLM
            response = self.llm_handler.query_to_llm(
                query=reformed_query if reformed_query is not None else data.query,
                context=retrieved_docs['documents'][0],
                histories=chat_histories
            )

            # Chat history 저장
            chat_history = {
                'user_query': data.query,
                'llm_response': response['answer'],
                'datetime': datetime.now()
            }
            self.state_handler.set_chat_history(state_data=chat_history)

            # User query caching
            chat_history.update({'questions': "|".join(response['questions'])})
            self.cache_handler.set_cache(collection_name=self.cache_collection_name, data=chat_history)

            # Return result
            return response

    async def make_chat(self, request, data):
        """
        SSE 방식의 응답
        :param request:
        :param data:
        :return:
        """
        # Check query cache
        caches = self.cache_handler.search_cache(
            query=data.query,
            collection_name=self.cache_collection_name
        )

        if caches is not None:
            cached_response = caches['metadatas'][0][0]['llm_response']

            chat_history = {
                'user_query': data.query,
                'llm_response': cached_response,
                'datetime': datetime.now()
            }
            # Chat history 저장
            self.state_handler.set_chat_history(state_data=chat_history)

            # Client에 stream 응답
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
            try:
                # Retrieve documents
                retrieved_docs = self.vectordb_handler.retrieve_documents(
                    query=data.query,
                    collection_name=self.collection_name,
                    n_results=3
                )

                # Get chat histories
                chat_histories = self.state_handler.get_chat_histories()

                # Reform user query
                reform_stream = await self.llm_handler.query_to_reform_stream(query=data.query, histories=chat_histories)
                reformed_query = ""
                async for chunk in reform_stream:
                    if chunk.choices[0].delta.content is not None:
                        reformed_query += chunk.choices[0].delta.content

                # Query LLM by stream
                stream = await self.llm_handler.query_to_llm_stream(
                    query=reformed_query if reformed_query.strip() != "" else data.query,
                    context=retrieved_docs['documents'][0],
                    histories=chat_histories
                )

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

                    elif chunk.choices[0].finish_reason == 'length':
                        raise LLMLengthOverError

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

            except Exception as ex:
                message_list = ['\n\n', '죄송합니다. 현재 답변을 생성할 수 없습니다.', '']
                exception_response = []
                for msg in message_list:
                    exception_response.append(ujson.dumps({
                        "id": 'Exception',
                        "model": 'cache',
                        "choices": [{
                            "delta": {
                                "role": None,
                                "content": msg
                            },
                            "finish_reason": '' if msg != '' else 'stop',
                            "index": 0
                        }]
                    }))
                for chunk in exception_response:
                    await asyncio.sleep(0.008)
                    yield f"data: {chunk}\n\n"

                error = await exception_handler(ex) if type(ex) is not APIException else ex
                await api_logger(request=request, error=error)

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