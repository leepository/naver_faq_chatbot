from fastapi import APIRouter

from app.domains.chatbot.apis import chatbot_router

domain_router = APIRouter()

domain_router.include_router(
    chatbot_router,
    prefix='/chatbot',
    tags=['ChatBot']
)

