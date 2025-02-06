import pandas as pd
import tqdm

from generator import get_llm_api
from langchain.prompts import ChatPromptTemplate
from omegaconf import DictConfig
from openai import OpenAI
from retrieval import ChromaRetrieval
from utils.generator_evaluate import evaluate_batch
from utils.set_seed import set_seed

client = OpenAI()


def generate(cfg: DictConfig):
    set_seed(cfg.seed)
    all_results = []

    # data
    data = pd.read_csv("eval_data_path")

    # retrieval = get_retriever(cfg)
    # retrieval - ChromaRetrieval 사용
    retriever = ChromaRetrieval(cfg)

    # llm
    system_template = cfg.chat_template
    model = get_llm_api(cfg)

    data = pd.read_csv(cfg.eval_data_path)

    all_results = []
    for _, row in tqdm.tqdm(data.iterrows(), desc="Processing Queries"):
        # dataset validation 수정필요
        query_result = {"query": row["question"]}

        docs = retriever.get_relevant_documents(row["question"])
        query_result["retrieved_docs"] = docs

        tem = ChatPromptTemplate.from_messages([("system", system_template), ("user", row["question"])])

        s = ""
        for i in range(len(docs)):
            s += docs[i].page_content

        prompt = tem.invoke({"docs": s})

        answer = model.invoke(prompt)

        query_result["answer"] = answer
        query_result["ground_truth"] = row["llm_text"]

        all_results.append(query_result)

    await evaluate_batch(all_results)
