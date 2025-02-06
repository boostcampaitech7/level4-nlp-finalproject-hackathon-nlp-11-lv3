from typing import List, Optional
import os
from langchain.docstore.document import Document
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

from retrieval.base import BaseRetriever
from utils.query_rewriter import QueryRewriter

class ChromaRetrieval(BaseRetriever):
    def __init__(self, cfg):
        self.base_path = './RAG/vector_db'
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=cfg.query_embedding_model_name,
            model_kwargs={'device': 'cuda'},
            encode_kwargs={'normalize_embeddings': True}
        )
        self.query_rewriter = QueryRewriter()
        self.db_cache = {}
        
    def _get_db(self, company: Optional[str] = None) -> Chroma:
        """특정 회사 또는 전체 데이터의 ChromaDB 인스턴스를 반환"""
        db_path = os.path.join(self.base_path, company if company else "All_data")
        
        if db_path not in self.db_cache:
            self.db_cache[db_path] = Chroma(
                persist_directory=db_path,
                embedding_function=self.embedding_model
            )
        
        return self.db_cache[db_path]
    
    def get_relevant_documents(self, query: str, k: int = 5) -> List[Document]:
        # 쿼리에서 회사명 추출
        rewritten_query, company = self.query_rewriter.extract_company(query)
        
        print("*******")
        print(company)
        print("*******")
        # 회사별 DB 또는 전체 DB에서 검색
        db = self._get_db(company)
        
        # 관련 문서 검색
        docs = []
        # for query in rewritten_query:
        #     docs.extend(db.similarity_search(query, k= 2*k // len(rewritten_query)))
        # mmr
        docs = db.max_marginal_relevance_search(query, k=k)
        
        return docs 