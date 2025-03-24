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

    def clear_chat_histories(self):
        try:
            self.handler.clear_chat_histories()
            return True

        except Exception as ex:
            print('[EX] ChatbotService.clear_chat_histories : {ex}')
            return False