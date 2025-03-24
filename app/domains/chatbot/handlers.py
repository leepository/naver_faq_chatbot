from app.domains.chatbot.externals.openai.openai_external import OpenAIExternal
from app.domains.chatbot.repositories.chroma.chroma_chatbot_repository import ChromaChatbotRepository


class ChatbotHandler:

    def __init__(self, chatbot_repository: ChromaChatbotRepository, openai_external: OpenAIExternal):
        self.repository = chatbot_repository
        self.openai_external = openai_external

    def retrieve_documents(self, query: str, collection_name: str, n_results: int = 5):
        return self.repository.retrieve_documents(
            query=query,
            collection_name=collection_name,
            n_results=n_results
        )

    def query_to_llm(self, query: str, context):
        messages = [
            {
                'role': 'system',
                'content': f"""당신은 CS 전문가입니다. 아래 내용을 참고하여 고객의 질문에 답변하세요. {context}"""
             },
            {
                'role': 'user',
                'content': query
            }
        ]

        response = self.openai_external.query(messages=messages)

        return response.choices[0].message.content
