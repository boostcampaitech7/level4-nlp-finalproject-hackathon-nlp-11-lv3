from typing import Any, Dict, List, Optional, Tuple

import os
import re
import time
from pathlib import Path

import hydra
import numpy as np
from generator import get_llm_api
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_models import ChatClovaX
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from rapidfuzz import process
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline
from loguru import logger

"""
기본적으로 gpt-4o-mini 모델을 사용하여 쿼리를 수정합니다.
"""
query_rewriting_prompt = """
당신은 쿼리를 재작성 해주는 전문가입니다.
다음 쿼리를 수정하여 더 정확한 검색을 위해 조금 더 구체적으로 작성하거나 분리해 주세요.
만약 쿼리에 리스트에 있는 회사명과 같은 회사명이 있으면 리스트의 이름으로 수정해주세요.
만약 없다면 None 을 반환해주세요.

List: {list}

예시)
INPUT: kakaobank 주가 예측
OUTPUT: 카카오뱅크 주가 예측

INPUT: 카카오뱅크와 네이버 주가 예측
OUTPUT: 카카오뱅크 주가 예측|네이버 주가 예측

INPUT: "없는회사명"과 네이버 주가 예측
OUTPUT: None|네이버 주가 예측

INPUT: "없는회사명"의 시가총액은?
OUTPUT: None

"""

project_root = Path(__file__).parent.parent


class QueryRewriter:
    def __init__(self):
        
        self.company_names = os.listdir(project_root / "vector_db")
        self.parser = StrOutputParser()
        self._load_config()
        self.model = get_llm_api(self.cfg, temperature=0.4)

    def _load_config(self):
        """Hydra 설정 로드"""
        
        # 상대 경로로 config_path 설정
        with hydra.initialize(version_base=None, config_path="../configs"):
            cfg = hydra.compose(config_name="config")
            self.cfg = cfg

    def extract_company(self, query: str) -> Tuple[str, Optional[str]]:
        """
        Args:
            query: 원본 쿼리 문자열

        Returns:
            Tuple[str, Optional[str]]: (수정된 쿼리, 회사명) 또는 (원본 쿼리, None)
        """
        # query 대문자로 변경
        query = query.upper()
        # 회사명 추출

        for company in self.company_names:
            if company in query:
                # 회사명을 쿼리에서 제거하고 공백 정리
                cleaned_query = re.sub(company, "", query).strip()
                return cleaned_query, company
        # fuzzy 회사명 추출
        matches = process.extract(query, self.company_names, limit=1)
        if matches and matches[0][1] >= 80:  # 80% 이상의 유사도를 가진 경우에만 매칭
            company = matches[0][0]
            # 회사명을 쿼리에서 제거하고 공백 정리
            cleaned_query = re.sub(company, "", query).strip()
            return cleaned_query, company
        # ner 회사명 추출후 유사도 기반 회사명 추출
        return query, None

    def rewrite_query(self, query: str) -> str:
        """
        쿼리를 수정하여 더 정확한 검색을 위해 조금 더 구체적으로 작성합니다.
        """
        start_time = time.time()
        #prompt = PromptTemplate(template=query_rewriting_prompt, input_variables=["query", "list"])
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", query_rewriting_prompt),
                ("user", "{query}"),
            ]
        )


        chain = prompt | self.model | self.parser
        # 회사명 리스트를 문자열로 변환
        company_list_str = ", ".join(f'"{company}"' for company in self.company_names)
        list_str = f"[{company_list_str}]"
        # 딕셔너리로 입력값 전달
        result = chain.invoke({"query": query, "list": list_str})
        # 결과가 리스트인 경우 문자열로 변환
        processing_time = time.time() - start_time
        logger.info(f"Rewrite Query processed in {processing_time:.2f} seconds")
        return result
