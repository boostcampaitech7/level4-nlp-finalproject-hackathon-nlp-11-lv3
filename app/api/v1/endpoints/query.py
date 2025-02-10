from core.auth import verify_credentials
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from schemas.rag import QueryRequest, QueryResponse
from services.rag_service import RAGService
import json
router = APIRouter()
rag_service = RAGService()


@router.post("", response_model=QueryResponse)
async def query(request: QueryRequest): #, username: str = Depends(verify_credentials)):
    try:
        #logger.info(f"Received query request from {username}: {request.query}")
        logger.info(f"Received query request: {request.query}")
        answer, retrieved_docs, processing_time, company = await rag_service.process_query(request)

        response = QueryResponse(
            answer=answer, context=retrieved_docs, processing_time=processing_time, company=company
        )
        logger.info(f"Query response: {response.answer}")
        #log 에 저장
        with open("result_log.txt", "a", encoding="utf-8") as f:
            f.write(f"{request.query}\n{response}\n--------------------------------\n")
        logger.info(f"Query processed successfully in {processing_time:.2f} seconds")
        return response

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")
