from app.domains.chatbot.handlers import ChatbotHandler

class ChatbotService:

    def __init__(self, chatbot_handler: ChatbotHandler):
        self.handler = chatbot_handler
        self.collection_name = 'naver_faq'

    def make_answer(self, data):

        # Retrieve documents
        retrieved_docs = self.handler.retreive_documents(
            query=data.query,
            collection_name=self.collection_name,
            n_results=3
        )
        print("retrieved_docs : ", retrieved_docs)

        # Query LLM

        # Return result
        return ""