from .bm25_retrieval import BM25Retrieval
from .chroma_retrieval import ChromaRetrieval
from .dense_retrieval import DenseRetrieval
from .ensemble_retrieval import EnsembleRetrieval

__all__ = ["DenseRetrieval", "BM25Retrieval", "EnsembleRetrieval"]


def get_retriever(cfg):
    if cfg.retriever_type == "dense":
        return DenseRetrieval(cfg).retriever
    elif cfg.retriever_type == "bm25":
        return BM25Retrieval(cfg).retriever
    elif cfg.retriever_type == "ensemble":
        return EnsembleRetrieval(retrievers=[DenseRetrieval(cfg), BM25Retrieval(cfg)], weights=[0.7, 0.3]).retriever
    else:
        raise ValueError(f"Unknown retriever type: {cfg.retriever_type}")
