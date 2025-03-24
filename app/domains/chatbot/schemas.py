from pydantic import BaseModel, Field

class ChatbotRequest(BaseModel):
    query: str = Field(description="LLM 질문 Query")
