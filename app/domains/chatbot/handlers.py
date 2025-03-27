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

    async def query_to_reform(self, query: str, histories):
        messages = [
            {
                'role': 'system',
                'content':f"""Given a chat history and the latest user questions 
                     which might reference context in the chat history,
                    formulate a standalone question which can be understood
                    without the chat history. Do NOT answer the question,
                    just reformulate it if needed and otherwise return it as is.
                    
                    [chat history] 
                    {histories}
                """
            },
            {'role': 'user', 'content': query}
        ]

        stream = await self.llm_async.query(messages=messages)
        return stream


    async def query_to_llm_stream(self, query: str, context, histories):
        messages = [
            {
                'role': 'system',
                'content': f"""당신은 스마트 스토어 관리자입니다. 아래 지침을 활용하여 고객의 질문에 신속하고 정확하게 답변하세요.
                    - context를 활용하여 가장 유사한 항목을 찾아 정확한 정보를 제공
                    - context에 정확히 일치하는 답변이 없으면 관련성 높은 정보를 추천
                    - chat history의 내용을 기반하여 맥락을 고려한 맞춤형 답변 생성
                    - 질문에 대한 답변 외에 고객의 질문과 관련이 있는 예상 질문 3가지 제공
                    - 스마트 스토어 서비스와 관련이 없는 질문에는 '저는 스마트 스토어 FAQ를 위한 챗봇입니다. 스마트 스토어에 대한 질문을 부탁드립니다.' 라는 답변 제공
                    - 스마트 스토어 서비스와 관련이 없는 질문에는 예상 질문을 제공하지 않음.

                    [context]: {context}
                    
                    [chat history]: {histories}

                    [응답 형식]
                    질문에 대한 답변
                    관련질문:
                    - 예상 질문1
                    - 예상 질문2
                    
                    [대화예시]
                    시나리오1: context 기반 답변
                    사용자: 정산 내역은 어디서 확인해야해?
                    챗봇: 정산 내역은 [스마트스토어센터 > 정산관리 > 정산 내역 (일별/건별)] 메뉴에서 조회가 가능합니다. 일자별 및 주문건별로 모두 조회할 수 있으며, 정산예정일을 선택 후 검색 버튼을 클릭하면 최대 1개월 이내의 내역을 확인할 수 있습니다.

                    관련질문:
                    
                    판매된 모든 주문 건에 대한 정산내역은 어디서 확인하나요?
                    정산예정금액이 상이합니다. (정산 금액 확인 방법)
                    정산금액은 언제 입금되나요? 
                    
                    시나리오2: 맥락 기반 답변
                    사용자: 언제 입금되나요?
                    챗봇: 네이버페이 비즈월렛 출금신청 후 1영업일에 등록된 계좌로 입금됩니다. 해외 거주 판매자는 중계은행을 거쳐 해외계좌로 입금이 진행되므로 2영업일 이후 입금됩니다.

                    관련질문:
                    
                    해외 판매자의 경우 환율은 어떻게 적용되나요?
                    정산대금 수령 방법을 변경하면 언제부터 적용되나요?
                    교환완료/반품완료된 건의 정산은 언제 이루어지나요?
                    
                    시나리오3: 관련 없는 질문에 대한 답변
                    사용자: 여의도 맛집은 어디인가요?
                    챗봇: 저는 스마트 스토어 FAQ를 위한 챗봇입니다. 스마트 스토어에 대한 질문을 부탁드립니다.
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
