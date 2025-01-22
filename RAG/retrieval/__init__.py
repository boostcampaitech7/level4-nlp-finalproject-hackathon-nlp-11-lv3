def get_retriever(cfg):
    if cfg.retriever_type == "dense":
        from RAG.retrieval.dense_retrieval import DenseRetriever

        return DenseRetriever(cfg).retriever
    elif cfg.retriever_type == "bm25":
        from RAG.retrieval.bm25_retrieval import BM25Retriever

        return BM25Retriever(cfg).retriever
    # elif model_source=="ensemble":
