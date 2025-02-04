from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from api.v1.endpoints import rag
from core.config import settings
from core.logging import setup_logging

app = FastAPI(
    title="RAG API Server",
    description="RAG(Retrieval Augmented Generation) API Server",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 메트릭스 설정
Instrumentator().instrument(app).expose(app)

# 로깅 설정
setup_logging()

# API 라우터 등록
app.include_router(rag.router, prefix="/api/v1", tags=["rag"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 