import os
import dotenv


dotenv.load_dotenv()

def get_llm_api(cfg):
    if cfg.llm_model_source == "openai":
        from langchain.llms import OpenAI

        return OpenAI(
            model=cfg.llm_model_name,
            api_key=os.getenv("OPENAI_API_KEY"),
        )  # temperature=0.5, max_tokens=1024

    elif cfg.llm_model_source == "naver":
        from langchain_community.chat_models import ChatClovaX
        return ChatClovaX(model="HCX-003", api_key=os.getenv("NAVER_API_KEY"))

    elif cfg.llm_model_source == "huggingface":
        return
