def get_embedding_model(cfg):
    if cfg.embedding_model_source == "huggingface":
        from langchain_community.embeddings import HuggingFaceEmbeddings

        embedding_model = HuggingFaceEmbeddings(
            model_name=cfg.embedding_model_name,
            model_kwargs={"device": "cuda", "trust_remote_code": True},
            encode_kwargs={"batch_size": cfg.batch_size},  # sentence_transformer 기준 32이가 기본값
        )
        return embedding_model

    elif cfg.embedding_model_sourcee == "openai":
        from langchain.embeddings import OpenAIEmbeddings

        return OpenAIEmbeddings(openai_api_key=cfg.openai_key, model=cfg.embedding_model_name)

    # elif cfg.embedding_model_source=="naver":
