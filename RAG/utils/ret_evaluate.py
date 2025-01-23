from datasets import concatenate_datasets, load_from_disk
from tqdm import tqdm


def ret_evaluate(retriever):
    dataset_dict = load_from_disk("/data/ephemeral/data/train_dataset")
    dataset1 = dataset_dict["train"].select(range(1000))
    dataset2 = dataset_dict["validation"]
    dataset_combined = concatenate_datasets([dataset1, dataset2])

    top1_count = 0
    top10_count = 0
    top20_count = 0
    top30_count = 0
    top40_count = 0
    top50_count = 0

    for i in tqdm(range(len(dataset_combined)), desc="retrieval eval"):
        question = dataset_combined[i]["question"]
        original_id = dataset_combined[i]["document_id"]

        topk_passages = retriever.get_relevant_documents(question, k=50)

        retrieved_id = [int(doc.metadata["document_id"]) for doc in topk_passages]

        if original_id == retrieved_id[0]:
            top1_count += 1
        if original_id in retrieved_id[:10]:
            top10_count += 1
        if original_id in retrieved_id[:20]:
            top20_count += 1
        if original_id in retrieved_id[:30]:
            top30_count += 1
        if original_id in retrieved_id[:40]:
            top40_count += 1
        if original_id in retrieved_id[:50]:
            top50_count += 1

    print(f"Top 1 Score: {top1_count / (i+1) * 100:.2f}%")
    print(f"Top 10 Score: {top10_count / (i+1) * 100:.2f}%")
    print(f"Top 20 Score: {top20_count / (i+1) * 100:.2f}%")
    print(f"Top 30 Score: {top30_count / (i+1) * 100:.2f}%")
    print(f"Top 40 Score: {top40_count / (i+1) * 100:.2f}%")
    print(f"Top 50 Score: {top50_count / (i+1) * 100:.2f}%")
