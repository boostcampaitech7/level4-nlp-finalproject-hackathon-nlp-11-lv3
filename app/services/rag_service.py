import time
from typing import List, Tuple
import hydra
from omegaconf import DictConfig
from loguru import logger
import sys
from pathlib import Path

from core.config import settings
from schemas.rag import RetrievalResult, QueryRequest

# RAG 모듈 import를 위한 경로 설정
rag_path = Path(__file__).parent.parent.parent
sys.path.append(str(rag_path))

# RAG 모듈 import
from RAG.retrieval import DenseRetrieval, BM25Retrieval, EnsembleRetrieval, ChromaRetrieval
from RAG.source.generate import generate

class RAGService:
    def __init__(self):
        """RAG 서비스 초기화"""
        self.cfg = self._load_config()
        self._init_retrievers()
        self._init_generator()
        
    def _load_config(self) -> DictConfig:
        """Hydra 설정 로드"""
        config_path = Path(settings.RAG_CONFIG_PATH).parent
        config_name = Path(settings.RAG_CONFIG_PATH).stem
        
        # Hydra 작업 디렉토리 설정
        with hydra.initialize(version_base=None, config_path=str(config_path)):
            cfg = hydra.compose(config_name=config_name)
            return cfg
    
    def _init_retrievers(self):
        """검색 모델 초기화"""
        try:
            # Dense Retrieval 초기화
            self.dense_retriever = DenseRetrieval(self.cfg)
            
            # BM25 Retrieval 초기화
            self.bm25_retriever = BM25Retrieval(self.cfg)
            
            # Ensemble Retrieval 초기화
            self.ensemble_retriever = EnsembleRetrieval(
                retrievers=[self.dense_retriever, self.bm25_retriever],
                weights=[0.7, 0.3]  # 가중치는 설정에 따라 조정 가능
            )
            
            logger.info("Successfully initialized all retrievers")
            
        except Exception as e:
            logger.error(f"Error initializing retrievers: {str(e)}")
            raise
    
    def _init_generator(self):
        """생성 모델 초기화"""
        try:
            self.generator = generate
            logger.info("Successfully initialized generator")
        except Exception as e:
            logger.error(f"Error initializing generator: {str(e)}")
            raise
    
    async def process_query(self, request: QueryRequest) -> Tuple[str, List[RetrievalResult], float]:
        """
        사용자 쿼리 처리
        
        Args:
            request: QueryRequest - 사용자 요청
            
        Returns:
            Tuple[str, List[RetrievalResult], float] - (답변, 검색된 문서들, 처리 시간)
        """
        start_time = time.time()
        
        try:
            # Ensemble 검색 수행
            logger.info(f"Retrieving documents for query: {request.query}")
            retrieved_docs = self.ensemble_retriever.retrieve(
                query=request.query,
                top_k=self.cfg.retrieval.top_k
            )
            
            # 답변 생성
            logger.info("Generating answer")
            answer = self.generator(
                self.cfg,
                query=request.query,
                context=retrieved_docs,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
            
            # 검색 결과 변환
            retrieval_results = [
                RetrievalResult(
                    content=doc.content,
                    score=float(doc.score),  # numpy.float32를 파이썬 float로 변환
                    source=str(doc.source)  # Path 객체를 문자열로 변환
                )
                for doc in retrieved_docs
            ]
            
            processing_time = time.time() - start_time
            logger.info(f"Query processed in {processing_time:.2f} seconds")
            
            return answer, retrieval_results, processing_time
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise 