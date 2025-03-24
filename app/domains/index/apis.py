from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from app.utils.common_utils import get_api_env

index_router = APIRouter()

@index_router.get(
    name='Application index',
    path='/',
    response_class=PlainTextResponse
)
async def index_api():
    """ Application index api """
    api_env = get_api_env()
    return f"[{api_env}] Naver faq chatbot ..."

@index_router.get(
    name='Application health check api',
    path='/health',
    response_class=PlainTextResponse
)
async def application_health_check_api():
    """ Application health check api """
    return 'ok'
