def get_llm_api(cfg):
    if cfg.llm_model_source == "openai":
        from langchain.llms import OpenAI

        return OpenAI(
            model=cfg.llm_model_name,
            api_key=cfg.oepnai_key,
        )  # temperature=0.5, max_tokens=1024

    elif cfg.llm_model_source == "naver":
        from langchain.llms.navermodel import NaverLLM

        return NaverLLM(model=cfg.llm_model_name, api_key="your_naver_api_key")

    elif cfg.llm_model_source == "huggingface":

        return
