from langchain.prompts import PromptTemplate
from langchain.smith import LangSmithSession
from langchain_core.output_parsers import StrOutputParser
from langsmith import traceable

# from langsmith.wrappers import wrap_openai
from omegaconf import DictConfig
from utils import set_seed

# from RAG.datasets import get_docs
from RAG.generator import get_llm_api
from RAG.source.retrieve import retrieve


@traceable(run_type="llm", metadata={"llm": "{llm_model}"})
def generate(cfg: DictConfig):
    set_seed(cfg.seed)

    # data

    # retrieval
    docs = retrieve(cfg)

    # docs relevant 검사 필요한지 체크 필요
    # docs reorder 필요한지 체크 필요

    # prompt template

    with LangSmithSession(project_name="RAG-Generation", metadata={"run_id": "example_run"}) as session:
        system_message = cfg.chat_template.format(docs="\n".join(docs))
        prompt = PromptTemplate(input_variables=["docs"], template=system_message)
        llm = get_llm_api(cfg)

        chain = prompt | llm | StrOutputParser()

        answer = session.run_chain(chain=chain, inputs={"docs": system_message}, metadata={"query": "example_query"})
        # 평가

        # 평가 결과 리턴
        return answer
