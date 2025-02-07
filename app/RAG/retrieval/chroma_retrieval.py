from typing import List, Optional

import os
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

import numpy as np
from langchain.docstore.document import Document
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from retrieval.base import BaseRetriever
from utils.query_rewriter import QueryRewriter


class ChromaRetrieval(BaseRetriever):
    def __init__(self, cfg):
        self.base_path = "./RAG/vector_db"
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=cfg.query_embedding_model_name,
            model_kwargs={"device": "cuda"},
            encode_kwargs={"normalize_embeddings": True, "batch_size": 32},  # 배치 처리 크기 설정
        )
        self.query_rewriter = QueryRewriter()
        self.db_cache = {}
        self.k = cfg.retrieval.get("top_k", 5)
        self.use_mmr = cfg.retrieval.get("use_mmr", True)  # MMR 사용 여부
        self.lambda_mult = cfg.retrieval.get("lambda_mult", 0.5)  # MMR 다양성 가중치
        self.executor = ThreadPoolExecutor(max_workers=4)  # 병렬 처리를 위한 스레드 풀

    @lru_cache(maxsize=1000)
    def _get_db(self, company: Optional[str] = None) -> Chroma:
        """특정 회사 또는 전체 데이터의 ChromaDB 인스턴스를 반환 (캐싱 적용)"""
        db_path = os.path.join(self.base_path, company if company else "All_data")

        if db_path not in self.db_cache:
            self.db_cache[db_path] = Chroma(persist_directory=db_path, embedding_function=self.embedding_model)

        return self.db_cache[db_path]

    def _search_with_mmr(self, db: Chroma, query: str, k: int) -> List[Document]:
        """MMR을 사용한 다양성 있는 검색 수행"""
        return db.max_marginal_relevance_search(
            query, k=k, fetch_k=2 * k, lambda_mult=self.lambda_mult  # 후보 문서 수 증가
        )

    def _search_with_similarity(self, db: Chroma, query: str, k: int) -> List[Document]:
        """기본 유사도 검색 수행"""
        return db.similarity_search(query, k=k)

    def get_relevant_documents(self, query: str, k: int = None) -> List[Document]:
        if k is None:
            k = self.k
        # 각 쿼리에 대해 검색 수행
        all_docs = []
        # search_func = self._search_with_mmr if self.use_mmr else self._search_with_similarity
        search_func = self._search_with_similarity
        rewritten_query = self.query_rewriter.rewrite_query(query)
        # 쿼리 분해
        """
        원본 쿼리: kakaobank 주가 예측
        수정된 쿼리: 1. 카카오뱅크 주가 예측, 2. 네이버 주가 예측
        """
        clean_query = rewritten_query.replace("수정된 쿼리: ", "")
        queries = []
        for q in clean_query.split("."):
            # 숫자와 공백 제거
            q = q.strip()
            if q.isdigit():
                continue
            queries.append(q[:-1])

        print("---------rewritten_query---------")
        print(queries)
        print("---------rewritten_query---------")
        if len(queries) == 1:
            # 쿼리에서 회사명 추출 및 쿼리 확장
            rewritten_queries, company = self.query_rewriter.extract_company(queries[0])
            if not isinstance(rewritten_queries, list):
                rewritten_queries = [rewritten_queries]

            # 회사별 DB 또는 전체 DB에서 검색
            db = self._get_db(company)

            def search_for_query(q):
                return search_func(db, q, k=(k // len(rewritten_queries)))

            # ThreadPoolExecutor를 사용하여 병렬 검색
            futures = [self.executor.submit(search_for_query, q) for q in rewritten_queries]
            for future in futures:
                all_docs.extend(future.result())
        else:
            # 여러 회사에 대한 쿼리 처리
            processed_queries = []
            companies = []

            for query in queries:  # original queries 사용
                query_text, company = self.query_rewriter.extract_company(query)
                if not isinstance(query_text, list):
                    query_text = [query_text]
                processed_queries.extend(query_text)
                companies.extend([company] * len(query_text))

            print("Companies:", companies)
            print("Processed queries:", processed_queries)

            # 회사별 DB 가져오기
            dbs = [self._get_db(company) for company in companies]

            def search_for_query(q, db):
                return self._search_with_mmr(db, q, k=k // len(processed_queries))

            # 각 쿼리-DB 쌍에 대해 검색 실행
            futures = [self.executor.submit(search_for_query, q, db) for q, db in zip(queries, dbs)]

            for future in futures:
                all_docs.extend(future.result())

        return all_docs
