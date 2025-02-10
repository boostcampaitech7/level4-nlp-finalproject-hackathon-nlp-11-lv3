from typing import List, Optional

import os
import time
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

import numpy as np
from langchain.docstore.document import Document
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain.vectorstores import Chroma
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from loguru import logger
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
        self.reranker = HuggingFaceCrossEncoder(model_name=cfg.retrieval.reranker_model_name)
        self.compressor = CrossEncoderReranker(model=self.reranker, top_n=15)

    @lru_cache(maxsize=1000)
    def _get_db(self, company: Optional[str] = None) -> Chroma:
        """특정 회사 또는 전체 데이터의 ChromaDB 인스턴스를 반환 (캐싱 적용)"""
        db_path = os.path.join(self.base_path, company if company else "All_data")

        if db_path not in self.db_cache:
            self.db_cache[db_path] = Chroma(persist_directory=db_path, embedding_function=self.embedding_model)

        return self.db_cache[db_path]

    def _search_with_mmr(self, db: Chroma, query: str, k: int, company: str) -> List[Document]:
        """MMR을 사용한 다양성 있는 검색 수행"""
        if company and company.lower() != "none":
            return db.max_marginal_relevance_search(query, k=k, filter={"company": company})
        else:
            return db.max_marginal_relevance_search(query, k=k)

    def _search_with_similarity(self, db: Chroma, query: str, k: int, company: str) -> List[Document]:
        """
        기본 유사도 검색 수행
        company가 none이면 전체 데이터베이스에서 검색
        """
        logger.info(f"Performing similarity search with query: {query}, company: {company}")
        if company and company.lower() != "none":
            logger.info(f"Applying company filter: {company}")
            return db.similarity_search(query, k=k, filter={"company": company})
        logger.info("No company filter applied, searching entire database")
        return db.similarity_search(query, k=k)

    def get_relevant_documents_without_query_rewritten(self, query: str, k: int = None) -> List[Document]:
        start_time = time.time()
        all_docs = []
        query_text, company = self.query_rewriter.extract_company(query)
        if not isinstance(query_text, list):
            query_text = [query_text]

        db = self._get_db("All_data")
        retriever = db.as_retriever()

        compression_retriever = ContextualCompressionRetriever(
            base_compressor=self.compressor, base_retriever=retriever
        )

        def search_for_query(q, company):
            if company:
                return compression_retriever.get_relevant_documents(q, k=k, filter={"company": company})
            else:
                return compression_retriever.get_relevant_documents(q, k=k)

        futures = [self.executor.submit(search_for_query, q, company) for q in query_text]
        for future in futures:
            all_docs.extend(future.result())
        logger.info(f"Retrieval processed without query rewritten in {time.time() - start_time:.2f} seconds")
        return all_docs

    def get_relevant_documents_with_query_rewritten(self, query: str, k: int = None) -> List[Document]:
        if k is None:
            k = self.k

        all_docs = []

        # 쿼리 리라이터를 통해 쿼리 수정
        rewritten_query = self.query_rewriter.rewrite_query(query)
        print(rewritten_query)
        # OUTPUT: 부분 추출
        clean_query = rewritten_query.split("OUTPUT:")[-1].strip()
        start_time = time.time()
        # None인 경우 처리 우선전체에서 검색.
        if clean_query == "None":
            retrieval_time = time.time() - start_time
            ret = self._search_with_similarity(self._get_db("All_data"), query, k, None)
            logger.info(f"Retrieval processed in {retrieval_time:.2f} seconds")
            return ret

        # 여러 회사에 대한 쿼리인 경우 파이프(|)로 분리
        queries = clean_query.split("|")
        logger.info(f"Parsed queries: {queries}")

        if len(queries) == 1:
            # 단일 쿼리 처리
            if queries[0].strip() == "None":
                retrieval_time = time.time() - start_time
                ret = self._search_with_similarity(self._get_db("All_data"), query, k, None)
                logger.info(f"Retrieval processed in {retrieval_time:.2f} seconds")
                return ret

            query_text, company = self.query_rewriter.extract_company(queries[0])
            if not isinstance(query_text, list):
                query_text = [query_text]

            db = self._get_db("All_data")
            retriever = db.as_retriever()

            compression_retriever = ContextualCompressionRetriever(
                base_compressor=self.compressor, base_retriever=retriever
            )

            def search_for_query(q, company):
                if company:
                    return compression_retriever.get_relevant_documents(q, k=k, filter={"company": company})
                else:
                    return compression_retriever.get_relevant_documents(q, k=k)

            futures = [self.executor.submit(search_for_query, q, company) for q in query_text]
            for future in futures:
                all_docs.extend(future.result())
        else:
            # 여러 쿼리 처리
            db = self._get_db("All_data")
            retriever = db.as_retriever()
            compression_retriever = ContextualCompressionRetriever(
                base_compressor=self.compressor, base_retriever=retriever
            )

            def search_for_query(q, k_per_query, company):
                if company:
                    return compression_retriever.get_relevant_documents(q, k=k_per_query, filter={"company": company})
                else:
                    return compression_retriever.get_relevant_documents(q, k=k_per_query)

            for query_part in queries:
                if query_part.strip() == "None":
                    continue

                query_text, company = self.query_rewriter.extract_company(query_part)
                if not isinstance(query_text, list):
                    query_text = [query_text]

                k_per_query = max(1, k // len(queries))
                future = self.executor.submit(search_for_query, query_text[0], k_per_query, company)
                # future = self.executor.submit(search_func, db, query_text[0], k_per_query, company)
                all_docs.extend(future.result())

        processing_time = time.time() - start_time
        logger.info(f"Retrieval processed in {processing_time:.2f} seconds")
        return all_docs

    def get_relevant_documents(self, query: str, k: int = None) -> List[Document]:
        """
        BaseRetriever의 추상 메서드 구현
        기본적으로 query rewritten을 사용하여 문서를 검색
        """
        return self.get_relevant_documents_with_query_rewritten(query, k)
