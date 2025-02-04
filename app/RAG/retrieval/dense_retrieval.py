# retrieval/dense_retriever.py
from typing import List
import os

from data import get_docs
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from retrieval.base import BaseRetriever
from retrieval.embedding_model import get_embedding_model
from retrieval.reranking import get_reranker_model


class DenseRetrieval(BaseRetriever):
    def __init__(self, cfg):
        self.vector_store_path = cfg.vector_store_path
        self.chunk_size = cfg.chunk_size
        self.documents = get_docs(cfg)
        self.chuck_overlap = cfg.chunk_overlap
        self.embedding_model = get_embedding_model(cfg)
        self.vector_store = self._load_or_create_vector_store()
        self.retriever = self.vector_store.as_retriever()
        if cfg.rerank:
            self.retriever = get_reranker_model(cfg, self.retriever)

    def _load_or_create_vector_store(self) -> FAISS:
        if os.path.exists(self.vector_store_path):
            vector_store = FAISS.load_local(
                self.vector_store_path, self.embedding_model, allow_dangerous_deserialization=True
            )
            return vector_store
        else:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chuck_overlap)
            split_docs = text_splitter.split_documents(self.documents)
            # cossine similarity
            vector_store = FAISS.from_documents(split_docs, self.embedding_model, metric="cosine")
            os.makedirs(self.vector_store_path, exist_ok=True)
            vector_store.save_local(self.vector_store_path)
            return vector_store

    def get_relevant_documents(self, query: str, k: int = 5) -> List[Document]:
        return self.retriever.get_relevant_documents(query, k=k)
