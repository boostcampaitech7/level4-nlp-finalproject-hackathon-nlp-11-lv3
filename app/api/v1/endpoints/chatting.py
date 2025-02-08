from fastapi import APIRouter, HTTPException
from loguru import logger
from schemas.rag import ChatRequest, ChatResponse
from services.rag_service import RAGService
from uuid import uuid4

router = APIRouter()
rag_service = RAGService()

@router.post("/", response_model=ChatResponse)
async def chatting(request: ChatRequest):
    try:
        # 세션 ID가 없으면 새로 생성
        session_id = request.session_id or str(uuid4())
        
        # 채팅 처리
        answer, retrieval_results, processing_time, company, current_chat_history = await rag_service.process_chat(
            session_id=session_id,
            query=request.query,
            llm_model=request.llm_model,
            chat_history=request.chat_history
        )
        
        return ChatResponse(
            session_id=session_id,
            answer=answer,
            company=company,
            retrieved_documents=retrieval_results,
            processing_time=processing_time,
            chat_history=current_chat_history
        )

    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")
