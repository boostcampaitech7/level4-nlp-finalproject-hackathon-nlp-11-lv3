# from langchain.smith import LangSmithSession
from omegaconf import DictConfig

from RAG.retrieval import get_retriever
from RAG.utils.ret_evaluate import ret_evaluate


def retrieve(cfg: DictConfig):
    retriever = get_retriever(cfg)

    # dataset 확정되면 llm까지 연결 + 실험
    # if cfg.mode == "inference": return retriever.get_relevant_documents(query, cfg.k)

    ret_evaluate(retriever)
