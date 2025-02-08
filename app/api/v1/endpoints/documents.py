from typing import List, Optional

import os
import shutil
from datetime import datetime
import time
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from loguru import logger
from schemas.rag import DocumentResponse
from services.pdf_service import PDFService

router = APIRouter()
rag_service = PDFService()

# PDF 저장 경로 설정
UPLOAD_DIR = "../PDF_OCR/pdf"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...), company: Optional[str] = Form(None)):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        
        # company가 None이면 기본 디렉토리 사용
        save_dir = os.path.join(UPLOAD_DIR, company) if company else UPLOAD_DIR
        os.makedirs(save_dir, exist_ok=True)
        
        file_path = os.path.join(save_dir, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        rag_service.process_pdf(file_path, company)
        
        return DocumentResponse(
            message="Document uploaded and processed successfully",
            filename=filename,
            company=company,
            upload_time=timestamp,
        )

    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")


@router.get("/", response_model=List[DocumentResponse])
async def list_documents():
    try:
        documents = await rag_service.list_documents()
        return documents
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")
