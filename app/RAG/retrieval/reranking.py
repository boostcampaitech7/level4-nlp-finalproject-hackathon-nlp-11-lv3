from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder


def get_reranker_model(cfg, retriever):
    model = HuggingFaceCrossEncoder(model_name=cfg.reranker_model_name)
    compressor = CrossEncoderReranker(model=model, top_n=10)
    compression_retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=retriever)
    return compression_retriever
