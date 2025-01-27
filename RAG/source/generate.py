from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langsmith import trace, traceable
from datasets import load_from_disk
from openai import OpenAI

# from langsmith.wrappers import wrap_openai
from omegaconf import DictConfig
from utils import set_seed

# from RAG.datasets import get_docs
from generator import get_llm_api
from source.retrieve import retrieve
'''
from confidentai.deepeval import (
    QAComparison,        
    PairwiseLLMComparison, 
    ChatRubricEval      
)
from typing import List, Dict
'''

client = OpenAI()

@traceable(run_type="RAG_pipeline_eval", metadata={"llm": "{llm_model}"})
def generate(cfg: DictConfig):
    set_seed(cfg.seed)

    # data
    dataset = load_from_disk("/data/ephemeral/data/train_dataset")# 자체 데이터 구축 후 수정
    
    # retrieval
    for query in tqdm.tqdm(dataset["validation"]["question"], desc="Processing Queries"):
        query_result = {"query": query}  # 쿼리별 결과 저장
        
        # Step 1: Retrieve Documents
        with trace("Retrieve Documents", run_type="retrieval") as retrieval_run:
            docs = retriever.get_relevant_documents(query)
            query_result["retrieved_docs"] = docs  # 검색된 문서 저장
            retrieval_run.end(inputs={"query": query}, outputs={"retrieved_docs": docs})
        
        # Step 2: Generate Response
        system_message = cfg.chat_template.format(docs="\n".join(docs))
        prompt = PromptTemplate(input_variables=["docs"], template=system_message)
        
        with trace("Generate Response", run_type="llm", metadata={"llm_model": cfg.llm_model}) as generation_run:
            chain = prompt | llm | StrOutputParser()
            answer = chain.invoke({"docs": system_message})
            query_result["generated_answer"] = answer  # 생성된 답변 저장
            generation_run.end(inputs={"docs": docs}, outputs={"answer": answer})
        
        # Step 3: Evaluate Generation
        with trace("Evaluate Response", run_type="evaluation") as eval_run:
            if "ground_truth" in query_result:  # 참조 답변(ground truth)이 있을 경우
                eval_scores = qa_eval.evaluate(
                    predictions=[answer],
                    references=[query_result["ground_truth"]]
                )
                query_result["eval_scores"] = eval_scores[0]  # 평가 점수 저장
                eval_run.end(inputs={"answer": answer}, outputs={"eval_scores": eval_scores})
            else:
                query_result["eval_scores"] = None  # 참조 답변 없으면 평가 건너뜀
        
        all_results.append(query_result)
    with trace("Retrieve Documents", run_type="retrieval") as retrieval_run:
        retriever = retrieve(cfg)
        docs = retriever.get_relevant_documents(query)
        retrieval_run.end(inputs={"query": cfg.query}, outputs={"retrieved_docs": docs})
    
    system_message = cfg.chat_template.format(docs="\n".join(docs))
    prompt = PromptTemplate(input_variables=["docs"], template=system_message)
    llm = get_llm_api(cfg)
    
    with trace("Generate Response", run_type="llm", metadata={"llm_model": cfg.llm_model}) as generation_run:
        chain = prompt | llm | StrOutputParser()

        answer = chain.invoke({"docs": system_message})
        chain.invoke({"docs": system_message})
    
