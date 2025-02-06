import time
from typing import List, Tuple, Optional
import hydra
from omegaconf import DictConfig
from loguru import logger
import sys
import os
from pathlib import Path
from langchain.prompts import ChatPromptTemplate
import json
from core.config import settings
from schemas.rag import RetrievalResult, QueryRequest
from RAG.generator import get_llm_api

# RAG 모듈 import를 위한 경로 설정
project_root = Path(__file__).parent.parent
rag_path = project_root / "RAG"
sys.path.append(str(rag_path))

# RAG 모듈 import
from RAG.retrieval import DenseRetrieval, BM25Retrieval, EnsembleRetrieval, ChromaRetrieval
#from RAG.source.generate import generate

class RAGService:
    def __init__(self):
        """RAG 서비스 초기화"""
        self._load_config()
        self._init_retrievers()
        self._init_generator()
        
    def _load_config(self):
        """Hydra 설정 로드"""
        # 현재 작업 디렉토리를 저장
        original_cwd = os.getcwd()
        
        try:
            os.chdir(str(project_root))
            
            # 상대 경로로 config_path 설정
            with hydra.initialize(version_base=None, config_path= "../RAG/configs"):
                cfg = hydra.compose(config_name="config")
                self.cfg = cfg
        finally:
            # 원래 디렉토리로 복귀
            os.chdir(original_cwd)
    
    def _init_retrievers(self):
        """검색 모델 초기화"""
        try:
            # # Dense Retrieval 초기화
            # self.dense_retriever = DenseRetrieval(self.cfg)
            
            # # BM25 Retrieval 초기화
            # self.bm25_retriever = BM25Retrieval(self.cfg)
            
            # # Ensemble Retrieval 초기화
            # self.ensemble_retriever = EnsembleRetrieval(
            #     retrievers=[self.dense_retriever, self.bm25_retriever],
            #     weights=[0.7, 0.3]  # 가중치는 설정에 따라 조정 가능
            # )
            self.ensemble_retriever = ChromaRetrieval(self.cfg)
            logger.info("Successfully initialized all retrievers")
            
        except Exception as e:
            logger.error(f"Error initializing retrievers: {str(e)}")
            raise
    
    def _init_generator(self):
        """생성 모델 초기화"""
        try:
            #self.generator = generate
            logger.info("Successfully initialized generator")
        except Exception as e:
            logger.error(f"Error initializing generator: {str(e)}")
            raise
    
    async def process_query(self, request: QueryRequest) -> Tuple[str, List[RetrievalResult], float, str]:
        """
        사용자 쿼리 처리
        
        Args:
            request: QueryRequest - 사용자 요청
            
        Returns:
            Tuple[str, List[RetrievalResult], float, str] - (답변, 검색된 문서들, 처리 시간, 회사명)
        """
        start_time = time.time()
        
        try:
            # Ensemble 검색 수행
            logger.info(f"Retrieving documents for query: {request.query}")
            retrieved_docs = self.ensemble_retriever.get_relevant_documents(
                query=request.query,
                #top_k=self.cfg.retrieval.top_k
                k = 10
            )
            # 검색된 문서들을 하나의 문자열로 결합
            docs_text = ""
            retrieval_results = []
            def fix_path(path: str) -> str:
                path = path.replace('page_page_', 'page_')
                if path.endswith('.json.json'):
                    path = path[:-5]  
                    
                return path
            cnt = 0
            for doc in retrieved_docs:
                if doc.metadata.get('category') == 'table':
                    cnt += 1
                    # path ocr_results/한화솔루션/한화솔루션_하나증권(2024.10.31)/page_page_2/5_table_2_result.json.json'
                    doc_path = doc.metadata.get('path')
                    # 마지막 확장자 제거
                    doc_path = fix_path(doc_path)
                    with open(os.path.join('../PDF_OCR' + doc_path), 'r') as f:
                        json_data = json.load(f)
                    html_text = json_data["content"]["html"]
                    docs_text += f"테이블 데이터 : {html_text}\n"
                    
                else:
                    docs_text += doc.page_content
                """
                metadat 예시 
                {
                    'category' : 'text',
                    'company' :  '네이버',
                    'date' : '2024.01.01',
                    'page' : '1',
                    'path' : 'data/path/to/file.pdf',
                    'securities' : 'SK증권'
                }
                """
                retrieval_results.append(
                    RetrievalResult(
                        content=doc.page_content,
                        metadata=doc.metadata,
                        score=float(doc.metadata.get('score', 1.0)),  # 기본값 1.0
                        company = doc.metadata.get('company', 'unknown'),
                        source = f"{doc.metadata.get('company', 'unknown')}_{doc.metadata.get('securities', 'unknown')}_{doc.metadata.get('date', 'unknown')}_page{doc.metadata.get('page', 'unknown')}_{doc.metadata.get('category', 'unknown')}"  # 기본값 'unknown'
                    )
                )
                if cnt == 1:
                    break
                    
            # print("#########################")
            # print(docs_text)
            # print("#########################")
            # ClovaX 모델 초기화 및 답변 생성
            llm = get_llm_api(self.cfg)
            
            # 프롬프트 템플릿 생성
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", self.cfg.chat_template),
                ("user", f"질문: {request.query}\n 참고 문서: {docs_text}")
            ])
            
            # 프롬프트 생성
            prompt = prompt_template.invoke({"docs": docs_text})
            
            # 답변 생성
            answer = llm.invoke(prompt)
            
            company = retrieval_results[0].company
            answer_text = answer.content
            
            logger.info("Successfully generated answer using ClovaX")
            processing_time = time.time() - start_time
            logger.info(f"Query processed in {processing_time:.2f} seconds")
            
            return answer_text, retrieval_results, processing_time, company
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise 