from typing import Optional

import asyncio
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from omegaconf import OmegaConf

# RAG 모듈 import
from app.RAG.utils.vector_store import VectorStore


class PDFService:
    def __init__(self):
        # 프로젝트 루트 디렉토리 설정 (app의 상위 디렉토리)
        self.base_dir = Path(__file__).parent.parent.parent
        self.pdf_ocr_dir = self.base_dir / "PDF_OCR"
        self.upload_dir = self.pdf_ocr_dir / "pdf"
        self.vector_db_dir = self.base_dir / "app/RAG/vector_db"
        self.executor = ThreadPoolExecutor(max_workers=1)

        # 필요한 디렉토리 생성
        self._create_directories()

        # 기본 설정 로드
        self.config = {
            "DIRS": {
                "input_dir": str(self.upload_dir),
                "output_dir": str(self.base_dir / "PDF_OCR/output"),
                "database_dir": str(self.base_dir / "PDF_OCR/database"),
                "ocr_output_dir": str(self.pdf_ocr_dir / "ocr_results"),
            },
            "MODEL": {
                "path": "~/.cache/huggingface/hub/models--juliozhao--DocLayout-YOLO-DocStructBench/snapshots/8c3299a30b8ff29a1503c4431b035b93220f7b11/doclayout_yolo_docstructbench_imgsz1024.pt",
                "imgsz": 1024,
                "line_width": 5,
                "font_size": 20,
                "conf": 0.2,
                "threshold": 0.05,
            },
        }

    def _create_directories(self):
        """필요한 디렉토리들을 생성합니다."""
        directories = [
            self.upload_dir,
            self.pdf_ocr_dir / "ocr_results",
            self.pdf_ocr_dir / "new_data",
            self.vector_db_dir,
            self.base_dir / "PDF_OCR/output",
            self.base_dir / "PDF_OCR/database",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    async def process_pdf_async(self, pdf_path: str, company: str) -> bool:
        """
        PDF를 비동기적으로 처리하고 Vector DB에 저장하는 전체 파이프라인을 실행합니다.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self.process_pdf, pdf_path, company)

    def process_pdf(self, pdf_path: str) -> bool:
        """
        PDF를 처리하고 Vector DB에 저장하는 전체 파이프라인을 실행합니다.

        Args:
            pdf_path (str): 업로드된 PDF 파일 경로
            company (str): 회사명

        Returns:
            bool: 처리 성공 여부
        """
        try:
            # 2. PDF_OCR 디렉토리로 이동하여 파이프라인 실행
            current_dir = os.getcwd()
            os.chdir(str(self.pdf_ocr_dir))

            # PDF 파싱 파이프라인 실행
            print("PDF 파싱 시작...")
            result = subprocess.run(
                ["python", "pdf_parser.py", "-i", "./pdf"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            print(result.stdout)
            if result.stderr:
                print("오류:", result.stderr)
            print("PDF 파싱 완료")

            print("Postprocessing 시작...")
            result = subprocess.run(
                ["python", "data_postprocess.py"], check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            print(result.stdout)
            if result.stderr:
                print("오류:", result.stderr)
            print("Postprocessing 완료")

            # 원래 디렉토리로 복귀
            os.chdir(current_dir)

            # 3. Vector DB 저장
            print("Vector DB 저장 중...")
            vector_store = VectorStore(
                OmegaConf.create({"passage_embedding_model_name": "nlpai-lab/KoE5"}), str(self.vector_db_dir)
            )

            # 회사별 및 전체 Vector DB 업데이트
            new_data_dir = self.pdf_ocr_dir / "new_data"
            vector_store.update_company_vector_stores(
                str(new_data_dir / "All_data/text_data.json"), str(new_data_dir / "All_data/table_data.json")
            )
            print("Vector DB 저장 완료")

            return True

        except subprocess.CalledProcessError as e:
            print(f"PDF 처리 중 명령어 실행 오류 발생: {str(e)}")
            print(f"오류 출력: {e.stderr}")
            return False
        except Exception as e:
            print(f"PDF 처리 중 오류 발생: {str(e)}")
            return False
        finally:
            # 작업 디렉토리를 원래대로 복원
            if "current_dir" in locals():
                os.chdir(current_dir)

    def clean_up(self):
        """임시 파일들을 정리합니다."""
        try:
            # PDF_OCR 디렉토리로 이동
            current_dir = os.getcwd()
            os.chdir(str(self.pdf_ocr_dir))

            # 임시 파일들 정리
            if self.upload_dir.exists():
                shutil.rmtree(self.upload_dir)

            # 필요한 디렉토리 재생성
            self._create_directories()

        except Exception as e:
            print(f"정리 중 오류 발생: {str(e)}")
        finally:
            # 작업 디렉토리를 원래대로 복원
            if "current_dir" in locals():
                os.chdir(current_dir)
