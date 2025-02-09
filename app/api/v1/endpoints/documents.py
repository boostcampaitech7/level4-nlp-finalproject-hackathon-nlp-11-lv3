from typing import List, Optional

import os
import shutil
import time
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile
from loguru import logger
from schemas.rag import DocumentResponse
from services.pdf_service import PDFService

router = APIRouter()
pdf_service = PDFService()

# PDF 저장 경로 설정
UPLOAD_DIR = "../PDF_OCR/pdf"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def process_pdf_background(file_path: str):
    """백그라운드에서 PDF를 처리하는 함수"""
    try:
        pdf_service.process_pdf(file_path)
    except Exception as e:
        logger.error(f"Background PDF processing error: {str(e)}")


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks, file: UploadFile = File(...), company: Optional[str] = Form(None)
):
    try:
        # 회사별 디렉토리 생성
        save_dir = os.path.join(UPLOAD_DIR)
        os.makedirs(save_dir, exist_ok=True)

        # 파일 저장
        filename = file.filename
        file_path = os.path.join(save_dir, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # PDF 처리를 백그라운드 작업으로 실행
        background_tasks.add_task(process_pdf_background, file_path)

        return DocumentResponse(
            message="Document uploaded and processing started", filename=filename, company=company, status="processing"
        )

    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")


@router.get("/", response_model=List[DocumentResponse])
async def list_documents():
    try:
        documents = []
        # 디렉토리 순회하여 문서 목록 생성
        for company in os.listdir(UPLOAD_DIR):
            company_dir = os.path.join(UPLOAD_DIR, company)
            if os.path.isdir(company_dir):
                for filename in os.listdir(company_dir):
                    if filename.lower().endswith(".pdf"):
                        documents.append(
                            DocumentResponse(
                                message="Document found", filename=filename, company=company, status="completed"
                            )
                        )
        return documents
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")
