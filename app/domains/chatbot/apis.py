from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from starlette.requests import Request

from app.container import Container
from app.domains.chatbot.schemas import ChatbotRequest, ExecutionResponse
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
        'answer': response['answer'],
        'questions': response['questions'],
        'related_question': response['related_question']
    }
    return response_dict

@chatbot_router.post(
    name='Naver FAQ Stream query',
    path='/chat'
)
@inject
async def naver_faq_chat_api(
        request: Request,
        data: ChatbotRequest,
        chatbot_service: ChatbotService = Depends(Provide[Container.chatbot_service])
):
    """ Naver FAQ 질문 API with stream """

    return StreamingResponse(
        chatbot_service.make_chat(request=request, data=data),
        media_type="text/event-stream",
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )

@chatbot_router.delete(
    name="Chat history 삭제",
    path='/chat-histories',
    response_model=ExecutionResponse
)
@inject
async def delete_chat_histories_api(
        chatbot_service: ChatbotService = Depends(Provide[Container.chatbot_service])
):
    """ 대화 이력 삭제 API """
    response = chatbot_service.clear_chat_histories()
    response_dict = {
        'result': response
    }

    return response_dict

@chatbot_router.delete(
    name="Cache clear",
    path="/cache-clear",
    response_model=ExecutionResponse
)
@inject
async def clear_cache_api(
        chatbot_service: ChatbotService = Depends(Provide[Container.chatbot_service])
):
    """ 캐시 클리어 """
    response = chatbot_service.clear_cache()
    response_dict = {
        'result': response
    }
    return response_dict
