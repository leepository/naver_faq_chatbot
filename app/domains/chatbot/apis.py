from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from app.container import Container
from app.domains.chatbot.schemas import ChatbotRequest
from app.domains.chatbot.services import ChatbotService

chatbot_router = APIRouter()

@chatbot_router.post(
    name='Naver FAQ Query',
    path='/ask'
)
@inject
async def naver_faq_ask_api(
        data: ChatbotRequest,
        chatbot_service: ChatbotService = Depends(Provide[Container.chatbot_service])
):
    """ Naver FAQ 질문 API """
    response = chatbot_service.make_answer(data=data)
    response_dict = {
        'answer': response
    }
    return response_dict
