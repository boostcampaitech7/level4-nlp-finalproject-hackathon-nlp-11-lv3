from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from loguru import logger
from typing import List, Optional
import shutil
import os
from datetime import datetime

from schemas.rag import DocumentResponse
from services.rag_service import RAGService

router = APIRouter()
rag_service = RAGService()

# PDF 저장 경로 설정
UPLOAD_DIR = "../PDF_OCR/pdf"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    company: Optional[str] = Form(None)
):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        await rag_service.process_document(file_path, company)
        
        return DocumentResponse(
            message="Document uploaded and processed successfully",
            filename=filename,
            company=company,
            upload_time=timestamp
        )
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading document: {str(e)}"
        )

@router.get("/", response_model=List[DocumentResponse])
async def list_documents():
    try:
        documents = await rag_service.list_documents()
        return documents
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing documents: {str(e)}"
        ) 