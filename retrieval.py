import os
import json

from dotenv import load_dotenv

from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
#from langchain.retrievers.document_compressors import CrossEncoderReranker
#from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers import BM25Retriever
#from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.smith import LangSmithSession, trace_function

def initialize_bm25_retriever(pickle_path, doc_list: List[str], k: int = 1) -> BM25Retriever:
    pickle_path = os.path.join(data_path, 'bm25_embeddings')
    if os.path.isfile(pickle_path):
        print(f"Loading BM25 index from {pickle_path}...")
        with open(pickle_path, "rb") as f:
            bm25_index = pickle.load(f)
        print("BM25 index loaded.")
    else:
        doc_list = [doc.page_content for doc in documents]
        print("Creating BM25 index...")
        bm25_index = BM25Okapi([doc.split() for doc in doc_list]) #tokenizer 수정 가능
        print("BM25 index created.")

        print(f"Saving BM25 index to {pickle_path}...")
        with open(pickle_path, "wb") as file:
            pickle.dump(bm25_index, file)
        print("BM25 index saved.")

    bm25_retriever = BM25Retriever(bm25_index, k=k)
    return bm25_retriever

def initialize_dense_retriever(vector_store_path, doc_list: List[str], embedding_model, k: int = 1) -> FAISS:
    if os.path.exists(vector_store_path):
        print("Loading existing vector store...")
        vector_store = FAISS.load_local(vector_store_path, embedding_model, allow_dangerous_deserialization=True)
    else:  
        print("Creating a new vector store...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        split_texts = text_splitter.split_documents(documents)
        vector_store = FAISS.from_documents(split_texts, embedding_model, index_factory="Flat")
        os.makedirs(vector_store_path, exist_ok=True)
        vector_store.save_local(vector_store_path)
        print(f"Vector store created and saved to {vector_store_path}.")

    return vector_store
    
def rerank_documents(query: str, retrieved_docs: List[str], reranker_model, top_k: int = 5) -> List[str]:

    query_doc_pairs = [(query, doc) for doc in retrieved_docs]
    scores = reranker_model.predict(query_doc_pairs)
    ranked_docs = sorted(zip(retrieved_docs, scores), key=lambda x: x[1], reverse=True)
    return [doc for doc, _ in ranked_docs[:top_k]]

@trace_function
def retrieve_documents(query, vector_store, k=5):
    retriever = vector_store.as_retriever(search_kwargs={"k": k})
    return retriever.get_relevant_documents(query)

if __name__ == "__main__":
    with LangSmithSession(name="main_workflow", project_name="LabQ-Finance-RAG") as session:  
        load_dotenv(dotenv_path="/data/ephemeral/level4-nlp-finalproject-hackathon-nlp-11-lv3/.env")
        LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        DATA_PATH = "/data/train_dataset/validation/wikipedia_documents.json"
        VECTOR_STORE_PATH = "/data/ephemeral/data"

        #ODQA datasets
        with open(json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        documents = [
            Document(
                page_content=content.get("text", ""), 
                metadata={
                    "title": content.get("title", "No Title"), 
                    "document_id": doc_id, 
                    "source": content.get("corpus_source", "Unknown Source")  
                }
            )
            for doc_id, content in data.items()
        ]

        embedding_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        vector_store = initialize_dense_retriever(vector_store_path, doc_list, embedding_model, k=dense_k)#추후 yaml or setup파일로 관리

        query = ""#"CJ제일제당의 2025년 매출액은 얼마로 예상되나요?"

        retrieved_docs = retrieve_documents(query, vector_store, k=5)#retrieve 방법에 따라 바뀌도록 수정 필요

        '''
        #ensemble_retrieval
        ensemble_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, dense_retriever],
            weights=weights
        )
        '''

        '''
        #cross_encoder_reranking
        re_ranker_model = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-v2-m3")
        compressor = CrossEncoderReranker(model=model, top_n=3)
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor, base_retriever=retriever
        )

        compressed_docs = compression_retriever.invoke(query)
        print("Generated Answer:", answer)
        '''

        session.log_event(
            "Answer generated", 
            {"query": query, "retrieved_docs": [doc.page_content for doc in retrieved_docs]}
        )
