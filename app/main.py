from api.v1.router import router as api_v1_router
from core.config import settings
from core.logging import setup_logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(
    title="RAG API Server",
    description="RAG(Retrieval Augmented Generation) API Server",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
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
app.include_router(api_v1_router, prefix="/api/v1")


# 헬스 체크 엔드포인트
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, workers=4)
