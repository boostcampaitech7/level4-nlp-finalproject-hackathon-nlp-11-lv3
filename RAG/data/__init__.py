def get_docs(cfg):
    if cfg.dataset == "ODQA":
        import json

        from langchain.docstore.document import Document

        with open(cfg.datapath, "r", encoding="utf-8") as f:
            data = json.load(f)

        documents = [
            Document(
                page_content=content.get("text", ""),
                metadata={
                    "title": content.get("title", "No Title"),
                    "document_id": doc_id,
                    "source": content.get("corpus_source", "Unknown Source"),
                },
            )
            for doc_id, content in data.items()
        ]
        return documents
    # elif dataset=="ours": 추후 작성
