import time
from typing import List, Dict, Any, Optional, Tuple
import re
import os
from rapidfuzz import process
import hydra
from pathlib import Path

from generator import get_llm_api
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline
import numpy as np
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_models import ChatClovaX
from langchain_core.documents import Document

"""
기본적으로 ClovaX 모델을 사용하여 쿼리를 수정합니다.


"""
query_rewriting_prompt = """
다음 쿼리를 수정하여 더 정확한 검색을 위해 조금 더 구체적으로 작성하거나 분리해 주세요.
만약 쿼리에 리스트에 있는 회사명과 같은 회사명이 있으면 리스트의 이름으로 수정해주세요.
{list}
예시)
원본 쿼리: kakaobank 주가 예측
수정된 쿼리: 카카오뱅크 주가 예측

원본 쿼리: 카카오뱅크와 네이버 주가 예측
수정된 쿼리: 1. 카카오뱅크 주가 예측, 2. 네이버 주가 예측


원본 쿼리: {query}
수정된 쿼리:
"""

project_root = Path(__file__).parent.parent
class QueryRewriter:
    def __init__(self):
        self.company_names = [
            "카카오뱅크", "엘앤에프", "롯데렌탈", "CJ제일제당", "LG화학",
            "네이버", "SK하이닉스", "한화솔루션", "SK케미칼", "크래프톤",
            
        ]
        
        self.parser = StrOutputParser()
        self._load_config()
        self.model = get_llm_api(self.cfg)
    def _load_config(self):
        """Hydra 설정 로드"""
        # 현재 작업 디렉토리를 저장
        original_cwd = os.getcwd()
        
        try:
            os.chdir(str(project_root))
            
            # 상대 경로로 config_path 설정
            with hydra.initialize(version_base=None, config_path= "../configs"):
                cfg = hydra.compose(config_name="config")
                self.cfg = cfg
        finally:
            # 원래 디렉토리로 복귀
            os.chdir(original_cwd)
    
    def extract_company(self, query: str) -> Tuple[str, Optional[str]]:
        """
        쿼리에서 회사명을 추출하고, 수정된 쿼리와 회사명을 반환합니다.
        
        Args:
            query: 원본 쿼리 문자열
            
        Returns:
            Tuple[str, Optional[str]]: (수정된 쿼리, 회사명) 또는 (원본 쿼리, None)
        """
        #query 대문자로 변경
        query = query.upper()
        # 회사명 추출
        
        for company in self.company_names:
            if company in query:
                # 회사명을 쿼리에서 제거하고 공백 정리
                cleaned_query = re.sub(company, '', query).strip()
                return cleaned_query, company
        # fuzzy 회사명 추출
        matches = process.extract(query, self.company_names, limit=1)
        if matches and matches[0][1] >= 80:  # 80% 이상의 유사도를 가진 경우에만 매칭
            company = matches[0][0]
            # 회사명을 쿼리에서 제거하고 공백 정리
            cleaned_query = re.sub(company, '', query).strip()
            return cleaned_query, company
        # ner 회사명 추출후 유사도 기반 회사명 추출
        return query, None

    def rewrite_query(self, query: str) -> str:
        """
        쿼리를 수정하여 더 정확한 검색을 위해 조금 더 구체적으로 작성합니다.
        """
        prompt = PromptTemplate(template=query_rewriting_prompt, input_variables=["query", "list"])
        chain = prompt | self.model | self.parser
        # 회사명 리스트를 문자열로 변환
        company_list_str = ', '.join(f'"{company}"' for company in self.company_names)
        list_str = f"[{company_list_str}]"
        # 딕셔너리로 입력값 전달
        result = chain.invoke({"query": query, "list": list_str})
        # 결과가 리스트인 경우 문자열로 변환
        return result



