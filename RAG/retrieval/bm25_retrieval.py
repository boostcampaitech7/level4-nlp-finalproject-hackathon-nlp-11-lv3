from typing import List

import os
import pickle

from data import get_docs
from langchain.docstore.document import Document
from rank_bm25 import BM25Okapi

from .base import BaseRetriever


class BM25Retriever(BaseRetriever):
    def __init__(self, cfg):
        self.pickle_path = cfg.vector_store_path
        self.bm25_index = self._load_or_create_bm25()
        self.documents = get_docs(cfg)

    def _load_or_create_bm25(self):
        if os.path.isfile(self.pickle_path):
            with open(self.pickle_path, "rb") as f:
                bm25_index = pickle.load(f)
        else:
            doc_texts = [doc.page_content for doc in self.documents]
            tokenized_docs = [text.split() for text in doc_texts]
            bm25_index = BM25Okapi(tokenized_docs)
            with open(self.pickle_path, "wb") as f:
                pickle.dump(bm25_index, f)
        return bm25_index

    def get_relevant_documents(self, query: str, k: int = 5) -> List[Document]:
        tokenized_query = query.split()
        scores = self.bm25_index.get_scores(tokenized_query)

        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]

        return [self.documents[i] for i in top_indices]
