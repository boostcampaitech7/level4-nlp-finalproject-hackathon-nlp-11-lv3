from typing import Optional

import os

import dotenv

dotenv.load_dotenv()


def get_llm_api(cfg, temperature: Optional[int] = 0.5):
    if cfg.llm_model_source == "openai":
        from langchain.chat_models import ChatOpenAI

        return ChatOpenAI(
            model=cfg.llm_model_name,
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=temperature,
        )  # temperature=0.5, max_tokens=1024

    elif cfg.llm_model_source == "naver":
        from langchain_community.chat_models import ChatClovaX

        from .ClovaStudioExcecutor import ClovaStudioExecutor

        os.environ["NCP_CLOVASTUDIO_API_KEY"] = os.getenv("NCP_CLOVASTUDIO_API_KEY")
        os.environ["NCP_CLOVASTUDIO_REQUEST_ID"] = os.getenv("NCP_CLOVASTUDIO_REQUEST_ID")
        os.environ["NCP_APIGW_API_KEY"] = os.getenv("NCP_APIGW_API_KEY")
        return ChatClovaX(
            model="HCX-003",
        )

    elif cfg.llm_model_source == "huggingface":
        return
