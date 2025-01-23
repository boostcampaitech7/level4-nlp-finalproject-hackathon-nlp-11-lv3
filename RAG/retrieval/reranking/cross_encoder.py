"""
def rerank_documents(query: str, retrieved_docs: List[str], reranker_model, top_k: int = 5) -> List[str]:

    query_doc_pairs = [(query, doc) for doc in retrieved_docs]
    scores = reranker_model.predict(query_doc_pairs)
    ranked_docs = sorted(zip(retrieved_docs, scores), key=lambda x: x[1], reverse=True)
    return [doc for doc, _ in ranked_docs[:top_k]]
"""
