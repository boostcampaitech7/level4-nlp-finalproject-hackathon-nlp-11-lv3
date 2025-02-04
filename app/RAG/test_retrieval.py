import hydra
from omegaconf import DictConfig
from pathlib import Path
from loguru import logger

from retrieval import DenseRetrieval, BM25Retrieval, EnsembleRetrieval

def test_retrievers(cfg: DictConfig):
    """
    각 retriever를 테스트합니다.
    """
    # Dense Retrieval 테스트
    logger.info("Testing Dense Retrieval...")
    dense_retriever = DenseRetrieval(cfg)
    dense_results = dense_retriever.get_relevant_documents(
        query="테스트 쿼리입니다.",
        k=3
    )
    logger.info(f"Dense Retrieval Results: {len(dense_results)} documents found")
    for doc in dense_results:
        logger.info(f"Score: {getattr(doc, 'score', 'N/A')}")
        logger.info(f"Content: {doc.page_content[:100]}...")
        logger.info("---")

    # BM25 Retrieval 테스트
    logger.info("\nTesting BM25 Retrieval...")
    bm25_retriever = BM25Retrieval(cfg)
    bm25_results = bm25_retriever.get_relevant_documents(
        query="테스트 쿼리입니다.",
        k=3
    )
    logger.info(f"BM25 Results: {len(bm25_results)} documents found")
    for doc in bm25_results:
        logger.info(f"Content: {doc.page_content[:100]}...")
        logger.info("---")

    # Ensemble Retrieval 테스트
    logger.info("\nTesting Ensemble Retrieval...")
    ensemble_retriever = EnsembleRetrieval(
        retrievers=[dense_retriever, bm25_retriever],
        weights=[0.7, 0.3]
    )
    ensemble_results = ensemble_retriever.get_relevant_documents(
        query="테스트 쿼리입니다.",
        k=3
    )
    logger.info(f"Ensemble Results: {len(ensemble_results)} documents found")
    for doc in ensemble_results:
        logger.info(f"Content: {doc.page_content[:100]}...")
        logger.info("---")

@hydra.main(version_base=None, config_path="configs", config_name="config")
def main(cfg: DictConfig):
    """
    메인 함수
    """
    try:
        test_retrievers(cfg)
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        raise

if __name__ == "__main__":
    main() 