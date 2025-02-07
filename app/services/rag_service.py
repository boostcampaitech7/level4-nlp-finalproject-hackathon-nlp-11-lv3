import time
from typing import List, Tuple, Optional
import hydra
from omegaconf import DictConfig
from loguru import logger
import pandas as pd
import sys
import os
from pathlib import Path
from langchain.prompts import ChatPromptTemplate
import json
from functools import lru_cache
import aiofiles
from io import StringIO
from prometheus_client import Counter, Histogram
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

# 메트릭 정의
QUERY_COUNTER = Counter('rag_query_total', 'Total number of RAG queries')
QUERY_LATENCY = Histogram('rag_query_latency_seconds', 'RAG query latency in seconds')
RETRIEVAL_LATENCY = Histogram('rag_retrieval_latency_seconds', 'Document retrieval latency')

class RAGService:
    def __init__(self):
        """RAG 서비스 초기화"""
        self._load_config()
        self._init_retrievers()
        self._init_generator()
        self._init_cache()
        
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
    
    def _init_cache(self):
        """캐시 초기화"""
        self.query_cache = {}
        
    @lru_cache(maxsize=1000)
    def _get_cached_retrieval(self, query: str) -> List[RetrievalResult]:
        """검색 결과 캐싱"""
        return self.ensemble_retriever.get_relevant_documents(
            query=query,
            k=15
        )

    async def process_query(self, request: QueryRequest) -> Tuple[str, List[RetrievalResult], float, str]:
        QUERY_COUNTER.inc()
        start_time = time.time()
        
        try:
            with RETRIEVAL_LATENCY.time():
                retrieved_docs = self._get_cached_retrieval(request.query)
            
            docs_text = ""
            retrieval_results = []
            
            async def process_doc(doc):
                retrieval_results.append(
                    RetrievalResult(
                        content=doc.page_content,
                        metadata=doc.metadata,
                        score=float(doc.metadata.get('score', 1.0)),
                        company=doc.metadata.get('company', 'unknown'),
                        source=f"{doc.metadata.get('company', 'unknown')}_{doc.metadata.get('securities', 'unknown')}_{doc.metadata.get('date', 'unknown')}_page{doc.metadata.get('page', 'unknown')}_{doc.metadata.get('category', 'unknown')}"
                    )
                )
                
                if doc.metadata.get('category') == 'table':
                    try:
                        doc_path = self._fix_path(doc.metadata.get('path'))
                        doc_path = '../PDF_OCR' + doc_path
                        table_path = doc_path.replace('.json', '.csv')
                        
                        if os.path.exists(table_path):
                            async with aiofiles.open(table_path, mode='r') as f:
                                content = await f.read()
                                df = pd.read_csv(StringIO(content))
                                return f"테이블 데이터 :\n {df.to_string(index=False)}\n"
                    except Exception as e:
                        logger.error(f"Error processing table document: {str(e)}")
                        return "테이블 데이터를 처리하는 중 오류가 발생했습니다."
                return doc.page_content
            
            # 병렬로 문서 처리
            from asyncio import gather
            processed_contents = await gather(*[process_doc(doc) for doc in retrieved_docs[:10]])
            docs_text = "\n".join(processed_contents)
            
            if not retrieval_results:  # retrieval_results가 비어있는 경우 처리
                logger.warning("No retrieval results found")
                company = "unknown"
            else:
                company = retrieval_results[0].company
            
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
            
            answer_text = answer.content
            
            logger.info(f"Successfully generated answer using {self.cfg.llm_model_name}")
            processing_time = time.time() - start_time
            logger.info(f"Query processed in {processing_time:.2f} seconds")
            
            return answer_text, retrieval_results, processing_time, company
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            raise
        finally:
            processing_time = time.time() - start_time
            QUERY_LATENCY.observe(processing_time)
            
        return answer_text, retrieval_results, processing_time, company

    def _fix_path(self, path: str) -> str:
        path = path.replace('page_page_', 'page_')
        if path.endswith('.json.json'):
            path = path[:-5]  
            
        return path
        