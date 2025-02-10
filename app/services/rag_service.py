from typing import Dict, List, Optional, Tuple

import json
import os
import sys
import time
import warnings
from functools import lru_cache
from io import StringIO
from pathlib import Path

import aiofiles
import hydra
import pandas as pd
from core.config import settings
from langchain.prompts import ChatPromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from loguru import logger
from omegaconf import DictConfig
from RAG.generator import get_llm_api
from schemas.rag import QueryRequest, RetrievalResult

warnings.filterwarnings("ignore")
# RAG 모듈 import를 위한 경로 설정
project_root = Path(__file__).parent.parent
rag_path = project_root / "RAG"
sys.path.append(str(rag_path))

# RAG 모듈 import
from RAG.retrieval import ChromaRetrieval

# from RAG.source.generate import generate

# 메트릭 정의


class RAGService:
    def __init__(self):
        """RAG 서비스 초기화"""
        self._load_config()
        self._init_retrievers()
        self._init_generator()
        self._init_cache()
        self._init_chat_histories()

    def _load_config(self):
        """Hydra 설정 로드"""
        # 현재 작업 디렉토리를 저장
        original_cwd = os.getcwd()

        try:
            os.chdir(str(project_root))

            # 상대 경로로 config_path 설정
            with hydra.initialize(version_base=None, config_path="../RAG/configs"):
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
            # self.generator = generate
            logger.info("Successfully initialized generator")
        except Exception as e:
            logger.error(f"Error initializing generator: {str(e)}")
            raise

    def _init_cache(self):
        """캐시 초기화"""
        self.query_cache = {}

    def _init_chat_histories(self):
        """채팅 기록 초기화"""
        self.chat_histories: Dict[str, ChatMessageHistory] = {}

    @lru_cache(maxsize=1000)
    def _get_cached_retrieval_with_query_rewritten(self, query: str) -> List[RetrievalResult]:
        """검색 결과 캐싱"""
        return self.ensemble_retriever.get_relevant_documents_with_query_rewritten(query=query, k=20)

    @lru_cache(maxsize=1000)
    def _get_cached_retrieval_without_query_rewritten(self, query: str) -> List[RetrievalResult]:
        """검색 결과 캐싱"""
        return self.ensemble_retriever.get_relevant_documents_without_query_rewritten(query=query, k=20)

    async def _retrieve_documents(self, query: str, is_rewritten: bool = True) -> Tuple[str, List[RetrievalResult]]:
        """문서 검색 로직"""
        if is_rewritten:
            retrieved_docs = self._get_cached_retrieval_with_query_rewritten(query)
        else:
            retrieved_docs = self._get_cached_retrieval_without_query_rewritten(query)
        docs_text = ""
        retrieval_results = []

        async def process_doc(doc):
            retrieval_results.append(
                RetrievalResult(
                    content=doc.page_content,
                    metadata=doc.metadata,
                    score=float(doc.metadata.get("score", 1.0)),
                    company=doc.metadata.get("company", "unknown"),
                    source=f"{doc.metadata.get('company', 'unknown')}_{doc.metadata.get('securities', 'unknown')}_{doc.metadata.get('date', 'unknown')}_page{doc.metadata.get('page', 'unknown')}_{doc.metadata.get('category', 'unknown')}",
                )
            )

            if doc.metadata.get("category") == "table":
                try:
                    doc_path = self._fix_path(doc.metadata.get("path"))
                    doc_path = "../PDF_OCR/processed_ocr_results" + doc_path
                    table_path = doc_path.replace(".json", ".csv")

                    if os.path.exists(table_path):
                        async with aiofiles.open(table_path, mode="r") as f:
                            content = await f.read()
                            df = pd.read_csv(StringIO(content))
                            return f"{doc.metadata.get('company')} 테이블 데이터 :\n {df.to_string(index=False)}\n"
                except Exception as e:
                    logger.error(f"Error processing table document: {str(e)}")
                    return "테이블 데이터를 처리하는 중 오류가 발생했습니다."
            return doc.page_content

        from asyncio import gather

        if len(retrieved_docs) > 7:
            processed_contents = await gather(*[process_doc(doc) for doc in retrieved_docs[:7]])
        else:
            processed_contents = await gather(*[process_doc(doc) for doc in retrieved_docs])
        docs_text = "\n".join(processed_contents)

        return docs_text, retrieval_results

    async def _generate_response(self, query: str, docs_text: str, llm_model: Optional[str] = None) -> str:
        """LLM 응답 생성 로직"""
        if llm_model == "GPT-4o-mini":
            self.cfg.llm_model_name = "gpt-4o-mini"
            self.cfg.llm_model_source = "openai"
            llm = get_llm_api(self.cfg)
        elif llm_model == "GPT-4o" or llm_model == None:
            self.cfg.llm_model_name = "gpt-4o"
            self.cfg.llm_model_source = "openai"
            llm = get_llm_api(self.cfg)
        elif llm_model == "CLOVA X":
            self.cfg.llm_model_source = "naver"
            llm = get_llm_api(self.cfg)
        else:
            raise ValueError(f"Invalid LLM model: {llm_model}")

        prompt_template = ChatPromptTemplate.from_messages(
            [("system", self.cfg.chat_template), ("user", f"질문: {query}")]
        )
        prompt = prompt_template.invoke({"docs": docs_text})
        start_time = time.time()
        answer = llm.invoke(prompt)
        # LLM response time log
        logger.info(f"LLM response time: {time.time() - start_time:.2f} seconds")
        return answer.content

    async def process_query(self, request: QueryRequest) -> Tuple[str, List[RetrievalResult], float, str]:
        """일반 쿼리 처리"""
        start_time = time.time()
        try:
            docs_text, retrieval_results = await self._retrieve_documents(request.query, False)

            if not retrieval_results:
                logger.warning("No retrieval results found")
                company = "unknown"
            else:
                company = retrieval_results[0].company

            answer_text = await self._generate_response(request.query, docs_text, request.llm_model)

            processing_time = time.time() - start_time
            logger.info(f"Query processed in {processing_time:.2f} seconds")

            return answer_text, retrieval_results, processing_time, company

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            raise
        finally:
            processing_time = time.time() - start_time

    async def process_chat(
        self, session_id: str, query: str, llm_model: str, chat_history: Optional[List[dict]] = None
    ) -> Tuple[str, List[RetrievalResult], float, str, List[dict]]:
        """채팅 처리"""
        #user query caching
        if session_id not in self.query_cache:
            self.query_cache[session_id] = []
        
        self.query_cache[session_id].append(query)
        if len(self.query_cache[session_id]) > 2:
            self.query_cache[session_id].pop(0)

        # 세션 기록 초기화 또는 가져오기
        if session_id not in self.chat_histories:
            self.chat_histories[session_id] = ChatMessageHistory()
            # 이전 대화 기록이 있다면 복원
            if chat_history:
                for msg in chat_history:
                    if isinstance(msg, dict):
                        role = msg.get("role")
                        content = msg.get("content")
                    else:
                        role = msg.role
                        content = msg.content

                    if role == "user":
                        self.chat_histories[session_id].add_user_message(content)
                    elif role == "assistant":
                        self.chat_histories[session_id].add_ai_message(content)

        chat_history = self.chat_histories[session_id]

        # 새 메시지 추가
        chat_history.add_user_message(query)

        try:
            # 문서 검색
            # 최근 두개의 질문을 합친 문장을 검색
            previous_user_query = ' '.join(self.query_cache[session_id])
            docs_text, retrieval_results = await self._retrieve_documents(previous_user_query + "\n" + query, True)

            if not retrieval_results:
                company = "unknown"
            else:
                company = retrieval_results[0].company

            # 채팅 컨텍스트를 포함한 프롬프트 생성
            chat_context = "\n".join(
                [
                    f"{'User' if isinstance(msg, HumanMessage) else 'Assistant'}: {msg.content}"
                    for msg in chat_history.messages[-4:]  # 최근 4개 메시지만 사용
                ]
            )

            # 응답 생성
            prompt_template = ChatPromptTemplate.from_messages(
                [
                    ("system", self.cfg.chatting_template),
                    ("system", "이전 대화 기록:\n{chat_context}"),
                    ("user", f"질문: {query}"),
                ]
            )

            if llm_model == "GPT-4o" or llm_model == "GPT-4o-mini":
                self.cfg.llm_model_name = "gpt-4o-mini"
                self.cfg.llm_model_source = "openai"
                llm = get_llm_api(self.cfg)
            elif llm_model == "CLOVA X":
                self.cfg.llm_model_source = "naver"
                llm = get_llm_api(self.cfg)
            else:
                raise ValueError(f"Invalid LLM model: {llm_model}")

            prompt = prompt_template.invoke({"docs": docs_text, "chat_context": chat_context})

            answer = llm.invoke(prompt)
            answer_text = answer.content

            # 응답 저장
            chat_history.add_ai_message(answer_text)

            # 현재 대화 기록을 ChatMessage 형식으로 변환
            current_chat_history = [
                {"role": "user" if isinstance(msg, HumanMessage) else "assistant", "content": msg.content}
                for msg in chat_history.messages
            ]

            processing_time = time.time()

            return answer_text, retrieval_results, processing_time, company, current_chat_history

        except Exception as e:
            logger.error(f"Error processing chat: {str(e)}", exc_info=True)
            raise

    def _fix_path(self, path: str) -> str:
        path = path.replace("page_page_", "page_")
        if path.endswith(".json.json"):
            path = path[:-5]
        return path
