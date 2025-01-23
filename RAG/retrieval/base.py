from typing import List

from abc import ABC, abstractmethod

from langchain.docstore.document import Document


class BaseRetriever(ABC):
    @abstractmethod
    def get_relevant_documents(self, query: str, k: int = 50) -> List[Document]:
        pass
