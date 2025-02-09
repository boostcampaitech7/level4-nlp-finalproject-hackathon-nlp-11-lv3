from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., description="메시지 작성자 역할 (user 또는 assistant)")
    content: str = Field(..., description="메시지 내용")


class QueryRequest(BaseModel):
    query: str = Field(..., description="사용자의 질문")
    llm_model: Optional[str] = Field(default="GPT-4o-mini", description="질문에 답변할 LLM")
    max_tokens: Optional[int] = Field(default=1000, description="생성할 최대 토큰 수")
    temperature: Optional[float] = Field(default=0.7, description="생성 텍스트의 다양성 (0.0 ~ 1.0)")
    company: Optional[str] = None


class RetrievalResult(BaseModel):
    content: str = Field(..., description="검색된 문서 내용")
    metadata: dict
    score: float = Field(..., description="검색 점수")
    company: str = Field(..., description="문서 소속 기업")
    source: str = Field(..., description="문서 출처")


class QueryResponse(BaseModel):
    answer: str = Field(..., description="생성된 답변")
    retrieved_documents: List[RetrievalResult] = Field(..., description="검색된 관련 문서들")
    processing_time: float = Field(..., description="처리 시간 (초)")
    company: Optional[str] = None


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    query: str = Field(..., description="사용자의 질문")
    llm_model: Optional[str] = Field(default="GPT-4o-mini", description="질문에 답변할 LLM")
    max_tokens: Optional[int] = Field(default=1000, description="생성할 최대 토큰 수")
    temperature: Optional[float] = Field(default=0.7, description="생성 텍스트의 다양성 (0.0 ~ 1.0)")
    company: Optional[str] = None
    chat_history: Optional[List[ChatMessage]] = Field(default=None, description="이전 대화 기록")


class ChatResponse(BaseModel):
    session_id: str = Field(..., description="채팅 세션 ID")
    answer: str = Field(..., description="생성된 답변")
    retrieved_documents: List[RetrievalResult] = Field(..., description="검색된 관련 문서들")
    processing_time: float = Field(..., description="처리 시간 (초)")
    company: Optional[str] = None
    chat_history: List[ChatMessage] = Field(..., description="현재까지의 전체 대화 기록")


class DocumentResponse(BaseModel):
    message: str
    filename: str
    company: Optional[str] = None
    upload_time: Optional[str] = None


class CompanyResponse(BaseModel):
    company: str = Field(..., description="기업 이름")
