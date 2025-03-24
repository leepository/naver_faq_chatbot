from pydantic import BaseModel, Field

class ChatbotRequest(BaseModel):
    query: str = Field(description="LLM 질문 Query")

class ExecutionResponse(BaseModel):
    result: bool = Field(description="수행 결과")
