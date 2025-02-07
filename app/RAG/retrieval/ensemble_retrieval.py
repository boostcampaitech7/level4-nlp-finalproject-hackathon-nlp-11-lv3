from typing import List

import numpy as np
from langchain.docstore.document import Document
from retrieval.base import BaseRetriever


class EnsembleRetrieval(BaseRetriever):
    def __init__(self, retrievers: List[BaseRetriever], weights: List[float] = None):
        self.retrievers = retrievers
        if weights is None:
            self.weights = [1.0] * len(self.retrievers)
        else:
            self.weights = weights

    def get_relevant_documents(self, query: str, k: int = 5) -> List[Document]:
        all_docs = []
        for retriever in self.retrievers:
            docs = retriever.get_relevant_documents(query, k)
            all_docs.extend(docs)

        unique_docs = list({doc.page_content: doc for doc in all_docs}.values())
        return unique_docs[:k]
