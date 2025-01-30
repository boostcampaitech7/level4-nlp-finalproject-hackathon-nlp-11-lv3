import tqdm
from datasets import load_from_disk
from generator import get_llm_api
from langchain.prompts import PromptTemplate
from omegaconf import DictConfig
from openai import OpenAI
from retrieval import get_retriever
from utils import set_seed
from utils.generator_evaluate import evaluate_batch

client = OpenAI()


def generate(cfg: DictConfig):
    set_seed(cfg.seed)
    all_results = []

    # data
    dataset = load_from_disk("/data/ephemeral/data/train_dataset")  # 자체 데이터 구축 후 수정

    # retrieval
    retriever = get_retriever(cfg)

    # llm
    model = get_llm_api(cfg)
    for item in tqdm.tqdm(dataset["validation"], desc="Processing Queries"):
        query_result = {"query": item["query"]}

        docs = retriever.get_relevant_documents(item["query"])
        query_result["retrieved_docs"] = docs

        system_message = cfg.chat_template.format(docs="\n".join(docs))
        prompt = PromptTemplate(input_variables=["docs"], template=system_message)

        answer = model.invoke(prompt)

        query_result["answer"] = answer
        query_result["ground_truth"] = item["answer"]

        all_results.append(query_result)

    evaluate_batch(all_results)
