import ujson

from app.domains.chatbot.externals.openai.openai_external import OpenAIExternal
from app.domains.chatbot.repositories.chroma.chroma_chatbot_repository import ChromaChatbotRepository
from app.domains.chatbot.repositories.state_repository import StateRepository


class ChatbotHandler:

    def __init__(
            self,
            chatbot_repository: ChromaChatbotRepository,
            openai_external: OpenAIExternal,
            internal_state_repository: StateRepository
    ):
        self.chroma_repository = chatbot_repository
        self.openai_external = openai_external
        self.internal_state_repository = internal_state_repository

    def retrieve_documents(self, query: str, collection_name: str, n_results: int = 5):
        return self.chroma_repository.retrieve_documents(
            query=query,
            collection_name=collection_name,
            n_results=n_results
        )

    def query_to_llm(self, query: str, context):

        histories = self.internal_state_repository.get_state()

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

        response = self.openai_external.query(messages=messages)
        llm_response = response.choices[0].message.content

        response_json = ujson.loads(llm_response)

        if response_json['related_question'] is True:
            chat_history = {
                'user_query': query,
                'llm_response': response_json['answer']
            }
            self.internal_state_repository.add_state(state_data=chat_history)

        return response_json

    def clear_chat_histories(self):
        self.internal_state_repository.clear_state()
