from fastapi import APIRouter, HTTPException
from loguru import logger

from schemas.rag import QueryRequest, QueryResponse
from services.rag_service import RAGService

router = APIRouter()
rag_service = RAGService()

@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    
    try:
        logger.info(f"Received query request: {request.query}")
        
        # RAG 서비스를 통한 쿼리 처리
        answer, retrieved_docs, processing_time, company = await rag_service.process_query(request)
        
        # 응답 생성
        response = QueryResponse(
            answer=answer,
            retrieved_documents=retrieved_docs,
            processing_time=processing_time,
            company=company
        )
        
        logger.info(f"Query processed successfully in {processing_time:.2f} seconds")
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        ) 