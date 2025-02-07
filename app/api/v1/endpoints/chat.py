from fastapi import APIRouter, HTTPException
from loguru import logger
from schemas.rag import ChatRequest, ChatResponse
from services.rag_service import RAGService

router = APIRouter()
rag_service = RAGService()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        logger.info(f"Received chat request: {request.query}")

        answer, retrieved_docs, processing_time, company = await rag_service.process_chat(request)

        response = ChatResponse(
            answer=answer, retrieved_documents=retrieved_docs, processing_time=processing_time, company=company
        )

        logger.info(f"Chat processed successfully in {processing_time:.2f} seconds")
        return response

    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")
