import ujson
from datetime import datetime
from app.domains.chatbot.handlers import ChatbotHandler

class ChatbotService:

    def __init__(self, chatbot_handler: ChatbotHandler):
        self.handler = chatbot_handler
        self.collection_name = 'naver_faq'

    def make_answer(self, data):

        # Retrieve documents
        retrieved_docs = self.handler.retrieve_documents(
            query=data.query,
            collection_name=self.collection_name,
            n_results=3
        )

        # Query LLM
        response = self.handler.query_to_llm(
            query=data.query,
            context=retrieved_docs['documents'][0]
        )

        # Return result
        return response

    async def make_chat(self, request, data):

        # Retrieve documents
        retrieved_docs = self.handler.retrieve_documents(
            query=data.query,
            collection_name=self.collection_name,
            n_results=3
        )

        # Query LLM by stream
        stream = await self.handler.query_to_llm_stream(query=data.query, context=retrieved_docs['documents'][0])

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
                self.handler.set_chat_history(state_data=chat_history)

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
            self.handler.clear_chat_histories()
            return True

        except Exception as ex:
            print('[EX] ChatbotService.clear_chat_histories : {ex}')
            return False