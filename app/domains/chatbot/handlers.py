import ujson
from datetime import datetime

from app.domains.chatbot.externals.llm_externals import LLMExternal
from app.domains.chatbot.repositories.state_repository import StateRepository
from app.domains.chatbot.repositories.vectordb_repository import VectordbRepository
from app.domains.chatbot.repositories.cache_repository import CacheRepository


class VectorDBHandler:

    def __init__(self, chatbot_repository: VectordbRepository):
        self.chroma_repository = chatbot_repository

    def retrieve_documents(self, query: str, collection_name: str, n_results: int = 5):
        return self.chroma_repository.retrieve_documents(
            query=query,
            collection_name=collection_name,
            n_results=n_results
        )

class StateHandler:

    def __init__(self, state_repository: StateRepository):
        self.state_repository = state_repository

    def get_chat_histories(self):
        raws = self.state_repository.get_state()
        histories = sorted(raws, key=lambda x: x['datetime'], reverse=True) if len(raws) > 0 else []
        return histories

    def set_chat_history(self, state_data):
        self.state_repository.add_state(state_data=state_data)

    def clear_chat_histories(self):
        self.state_repository.clear_state()


class LLMHandler:

    def __init__(self, llm_external: LLMExternal, llm_async_external: LLMExternal):
        self.llm = llm_external
        self.llm_async = llm_async_external

    def query_to_llm(self, query: str, context, histories):
        messages = [
            {
                'role': 'system',
                'content': f"""당신은 CS 전문가입니다. 연관 문서와 대화 이력을 참고하여 아래와 같은 기준으로 고객의 질문에 답변하세요
                    - 연관 문서와 관련이 없는 질문에는 '저는 스마트 스토어 FAQ를 위한 챗봇입니다. 스마트 스토어에 대한 질문을 부탁드립니다.' 라고 답변하세요.
                    - 연관 문서와 관련이 없는 질문에는 예상 질문이 없습니다.
                    - 연관 문서와 관련이 없는 질문의 경우에는 응답 형식 중 related_question 값으로 false를 반환해 주세요.
                    - 질문에 대한 답변 외에 고객의 질문과 관련이 있는 예상 질문 3가지를 추가해 주세요
                    - 연관 문서와 관련이 있는 질문의 경우에는 응답 형식 중 related_question 값으로 true를 반환해 주세요.
                    - JSON 형식으로 답변해 주세요


                    연관 문서: {context}

                    대화 이력: {histories}

                    응답 형식:
                    {{
                        "answer": "질문에 대한 답변",
                        "questions": ["예상 질문1", "예상 질문2"],
                        "related_question": "스마트 스토어와의 연관성"
                    }}
                """
            },
            {
                'role': 'user',
                'content': query
            }
        ]

        response = self.llm.query(messages=messages)
        llm_response = response.choices[0].message.content

        response_json = ujson.loads(llm_response)

        return response_json

    async def query_to_llm_stream(self, query: str, context, histories):
        messages = [
            {
                'role': 'system',
                'content': f"""당신은 CS 전문가입니다. 연관 문서와 대화 이력을 참고하여 아래와 같은 기준으로 고객의 질문에 답변하세요
                    - 인사나 안부를 묻는 질문에는 '안녕하세요. 무엇을 도와드릴까요?' 라고 답변하세요.
                    - 대화 이력과 관련이 있는 답변을 우선 고려하고 연관 문서를 참고하여 답변하세요.
                    - 대화 이력을 참고할때는 가장 최근것을 우선적으로 참고해 주세요.
                    - 질문에 대한 답변 외에 고객의 질문과 관련이 있는 예상 질문 3가지를 추가해 주세요
                    - 연관 문서와 관련이 없는 질문에는 '저는 스마트 스토어 FAQ를 위한 챗봇입니다. 스마트 스토어에 대한 질문을 부탁드립니다.' 라고 답변하세요.
                    - 연관 문서와 관련이 없는 질문에는 예상 질문이 없습니다. 

                    [연관 문서] {context}

                    [대화 이력] {histories}

                    [응답 형식]
                    "질문에 대한 답변"
                    관련질문:
                    - 예상 질문1
                    - 예상 질문2
                """
            },
            {
                'role': 'user',
                'content': query
            }
        ]

        stream = await self.llm_async.query(messages=messages)
        return stream


class CacheHandler:

    def __init__(self, cache_repository: CacheRepository):
        self.cache_repository = cache_repository

    def set_cache(self, collection_name: str, data: dict):
        self.cache_repository.add_cache(
            collection_name=collection_name,
            user_query=data['user_query'],
            metadata={
                "llm_response": data['llm_response'],
                "questions": data['questions'] if 'questions' in data else ''
            }
        )

    def search_cache(self, collection_name: str, query: str):
        docs = self.cache_repository.search_cache(collection_name=collection_name, query=query)
        return docs

    def clear_cache(self, collection_name: str):
        self.cache_repository.clear_cache(collection_name=collection_name)
