import tqdm
from datasets import load_from_disk
from generator import get_llm_api
from langchain.prompts import ChatPromptTemplate
from omegaconf import DictConfig
from openai import OpenAI
from retrieval import get_retriever
from utils.set_seed import set_seed
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
    system_template = cfg.chat_template
    model = get_llm_api(cfg)

    
    for item in tqdm.tqdm(dataset["validation"], desc="Processing Queries"):
        # dataset validation 수정필요
        query_result = {"query": item["query"]}

        docs = retriever.get_relevant_documents(item["query"])
        query_result["retrieved_docs"] = docs

        tem = ChatPromptTemplate.from_messages([("system", system_template), ("user", item["query"])])

        s = ""
        for i in range(len(docs)):
            s += docs[i].page_content

        prompt = tem.invoke({"docs": s})

        answer = model.invoke(prompt)

        query_result["answer"] = answer
        query_result["ground_truth"] = item["answer"]

        all_results.append(query_result)

    evaluate_batch(all_results)
