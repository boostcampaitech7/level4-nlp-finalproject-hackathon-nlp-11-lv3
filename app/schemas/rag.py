from pydantic import BaseModel, Field
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str = Field(..., description="사용자의 질문")
    max_tokens: Optional[int] = Field(default=1000, description="생성할 최대 토큰 수")
    temperature: Optional[float] = Field(default=0.7, description="생성 텍스트의 다양성 (0.0 ~ 1.0)")

class RetrievalResult(BaseModel):
    content: str = Field(..., description="검색된 문서 내용")
    score: float = Field(..., description="검색 점수")
    source: str = Field(..., description="문서 출처")

class QueryResponse(BaseModel):
    answer: str = Field(..., description="생성된 답변")
    retrieved_documents: List[RetrievalResult] = Field(..., description="검색된 관련 문서들")
    processing_time: float = Field(..., description="처리 시간 (초)") 