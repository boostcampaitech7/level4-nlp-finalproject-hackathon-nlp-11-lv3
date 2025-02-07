from api.v1.endpoints import chat, documents, query
from fastapi import APIRouter

router = APIRouter()

# 각 엔드포인트 라우터 등록
router.include_router(chat.router, prefix="/chat", tags=["chat"])
router.include_router(query.router, prefix="/query", tags=["query"])
router.include_router(documents.router, prefix="/documents", tags=["documents"])
