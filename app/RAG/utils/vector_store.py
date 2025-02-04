import os
import json
import shutil
from typing import List, Dict
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document
from tqdm import tqdm
from omegaconf import DictConfig

class VectorStore:
    def __init__(self, cfg: DictConfig, persist_directory: str = "vector_db"):
        """
        벡터 스토어 초기화
        Args:
            cfg (DictConfig): 설정 파일
            persist_directory (str): 벡터 DB를 저장할 디렉토리 경로
        """
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(
            model_name=cfg.embedding_model_name,
            model_kwargs={'device': 'cuda'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
    def load_json_data(self, json_path: str) -> List[Dict]:
        """JSON 파일에서 데이터를 로드합니다."""
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    def create_documents(self, data: List[Dict]) -> List[Document]:
        """
        데이터를 Document 객체로 변환합니다.
        """
        documents = []
        for item in data:
            # 메타데이터 생성
            metadata = {
                "company": item["company"],
                "securities": item["securities"],
                "category": item["category"],
                "page": item["page"],
                "date": item["date"],
                "path": item["path"]
            }
            
            # Document 객체 생성
            doc = Document(
                page_content=item["description"],
                metadata=metadata
            )
            documents.append(doc)
        return documents
        
    def update_company_vector_stores(self, text_json_path: str, table_json_path: str):
        """
        회사별로 벡터 DB를 업데이트합니다.
        """
        # JSON 데이터 로드
        text_data = self.load_json_data(text_json_path)
        table_data = self.load_json_data(table_json_path)
        
        # 모든 데이터 통합
        all_data = text_data + table_data
        
        # 회사별로 데이터 그룹화
        company_data = {}
        for item in all_data:
            company = item["company"]
            if company not in company_data:
                company_data[company] = []
            company_data[company].append(item)
            
        # 회사별로 벡터 DB 업데이트
        for company, data in tqdm(company_data.items(), desc="회사별 벡터 DB 업데이트 중"):
            company_persist_dir = os.path.join(self.persist_directory, company)
            
            # Document 객체 생성
            documents = self.create_documents(data)
            
            # 기존 벡터 DB가 있으면 추가, 없으면 새로 생성
            if os.path.exists(company_persist_dir):
                vectorstore = Chroma(
                    persist_directory=company_persist_dir,
                    embedding_function=self.embeddings
                )
                vectorstore.add_documents(documents)
            else:
                vectorstore = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    persist_directory=company_persist_dir
                )
            
            vectorstore.persist()
            print(f"{company} 벡터 DB 업데이트 완료: {len(documents)}개 문서 추가")
            
    def load_company_vectorstore(self, company: str) -> Chroma:
        """
        특정 회사의 벡터 DB를 로드합니다.
        """
        company_persist_dir = os.path.join(self.persist_directory, company)
        if not os.path.exists(company_persist_dir):
            raise ValueError(f"Vector store for company {company} does not exist")
            
        return Chroma(
            persist_directory=company_persist_dir,
            embedding_function=self.embeddings
        )

    @staticmethod
    def move_to_old_data(json_paths: List[str], old_data_dir: str = "old_data"):
        """처리된 JSON 파일을 old_data 디렉토리로 이동합니다."""
        if not os.path.exists(old_data_dir):
            os.makedirs(old_data_dir)
            
        for json_path in json_paths:
            if os.path.exists(json_path):
                filename = os.path.basename(json_path)
                target_path = os.path.join(old_data_dir, filename)
                shutil.move(json_path, target_path)
                print(f"파일 이동 완료: {json_path} -> {target_path}") 