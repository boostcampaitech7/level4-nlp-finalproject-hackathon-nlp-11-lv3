import time
from typing import List, Dict, Any, Optional, Tuple
import re
import os
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
다음 쿼리를 수정하여 더 정확한 검색을 위해 조금 더 구체적으로 작성해주세요.

원본 쿼리: {query}
수정된 쿼리:
"""

query_decompose_prompt = """
다음 쿼리를 더 작은 단위로 분해해주세요. 만약 분해할 필요가 없는 쿼리라면 원본 쿼리를 그대로 반환해주세요.
예시)
원본 쿼리: 카카오뱅크와 네이버 주가 예측
분해된 쿼리: 카카오뱅크 주가 예측, 네이버 주가 예측

원본 쿼리: 카카오뱅크 주가 예측
분해된 쿼리: 카카오뱅크 주가 예측

원본 쿼리: {query}
분해된 쿼리:
"""



class QueryRewriter:
    def __init__(self):
        self.company_names = [
            "카카오뱅크", "엘앤에프", "롯데렌탈", "CJ제일제당", "LG화학",
            "네이버", "SK하이닉스", "한화솔루션", "SK케미칼", "크래프톤"
        ]
        self.model = ChatClovaX(model_name="HCX-003", clovastudio_api_key = os.getenv("NCP_CLOVASTUDIO_API_KEY"))
        self.parser = StrOutputParser()

    def extract_company(self, query: str) -> Tuple[str, Optional[str]]:
        """
        쿼리에서 회사명을 추출하고, 수정된 쿼리와 회사명을 반환합니다.
        
        Args:
            query: 원본 쿼리 문자열
            
        Returns:
            Tuple[str, Optional[str]]: (수정된 쿼리, 회사명) 또는 (원본 쿼리, None)
        """
        for company in self.company_names:
            if company in query:
                # 회사명을 쿼리에서 제거하고 공백 정리
                cleaned_query = re.sub(company, '', query).strip()
                return cleaned_query, company
        
        return query, None 
    
    def rewrite_query(self, query: str) -> str:
        """
        쿼리를 수정하여 더 정확한 검색을 위해 조금 더 구체적으로 작성합니다.
        """
        prompt = PromptTemplate(template=query_rewriting_prompt, input_variables=["query"])
        chain = prompt | self.model | self.parser
        return chain.invoke(query)
    
    def decompose_query(self, query: str) -> List[str]:
        """
        쿼리를 더 작은 단위로 분해합니다.
        """
        prompt = PromptTemplate(template=query_decompose_prompt, input_variables=["query"])
        chain = prompt | self.model | self.parser
        return chain.invoke(query)


# class MultiqueryRetrieval:
#     def __init__(self):
#         self.model = ChatClovaX(model_name="clova/clova-x-large-v2")
#         self.parser = StrOutputParser()
#         self.prompt = PromptTemplate(template=query_rewriting_prompt, input_variables=["query"])
#         self.decompose_prompt = PromptTemplate(template=query_decompose_prompt, input_variables=["query"])
        
        