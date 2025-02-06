# from langchain.smith import LangSmithSession
from omegaconf import DictConfig
from retrieval import get_retriever
from utils.ret_evaluate import ret_evaluate_acc, ret_evaluate_geval
from utils.set_seed import set_seed


def retrieve(cfg: DictConfig):
    set_seed(cfg.seed)

    retriever = get_retriever(cfg)

    # dataset 확정되면 llm까지 연결 + 실험
    # if cfg.mode == "inference": return retriever.get_relevant_documents(query, cfg.k)

    if cfg.g_eval:
        ret_evaluate_geval(retriever, cfg)
    else:
        ret_evaluate_acc(retriever)
