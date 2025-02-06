import asyncio
import json

import pandas as pd
from datasets import concatenate_datasets, load_from_disk
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from langsmith import traceable
from tqdm import tqdm


def ret_evaluate_acc(retriever):
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


def ret_evaluate_geval(retriever, cfg):
    model = "gpt-4o-mini"
    Generation_criteria = [
        {
            "name": "Similarity",
            "description": "Do any of the retrieved contexts show strong similarity to the Ground Truth?",
            "weight": 5,
        },
        {
            "name": "Essentiality",
            "description": (
                "Do the retrieved contexts collectively capture " "essential information from the Ground Truth?"
            ),
            "weight": 5,
        },
        {
            "name": "Coverage",
            "description": "Do the retrieved contexts sufficiently address the user’s question?",
            "weight": 4,
        },
        {
            "name": "Relevance",
            "description": "Are all retrieved contexts relevant to the Ground Truth or the user’s query?",
            "weight": 3,
        },
        {
            "name": "Conciseness",
            "description": (
                "Does the combined length and number of retrieved contexts remain "
                "reasonable without overwhelming the user with excessive or irrelevant details?"
            ),
            "weight": 3,
        },
    ]

    metric1 = GEval(
        name=Generation_criteria[0]["name"],
        criteria=Generation_criteria[0]["description"],
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
        model=model,
        threshold=0.0,
    )
    metric2 = GEval(
        name=Generation_criteria[1]["name"],
        criteria=Generation_criteria[1]["description"],
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
        model=model,
        threshold=0.0,
    )
    metric3 = GEval(
        name=Generation_criteria[2]["name"],
        criteria=Generation_criteria[2]["description"],
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
        model=model,
        threshold=0.0,
    )
    metric4 = GEval(
        name=Generation_criteria[3]["name"],
        criteria=Generation_criteria[3]["description"],
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
        model=model,
        threshold=0.0,
    )
    metric5 = GEval(
        name=Generation_criteria[4]["name"],
        criteria=Generation_criteria[4]["description"],
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
        model=model,
        threshold=0.0,
    )

    async def get_metric_evaluations(test_case: LLMTestCaseParams) -> list:
        return await asyncio.gather(
            metric1.a_measure(test_case),  # 비동기 지원
            metric2.a_measure(test_case),
            metric3.a_measure(test_case),
            metric4.a_measure(test_case),
            metric5.a_measure(test_case),
        )

    async def evaluate_single_sample(question: str, docs: list, ground_truth: list) -> dict:
        actual_output = ", ".join([f"문서{i+1}: {doc}" for i, doc in enumerate(docs)])
        test_case = LLMTestCase(input=question, actual_output=actual_output, expected_output=ground_truth)

        eval_result = await get_metric_evaluations(test_case)
        evaluation_result = {
            "question": question,
            "docs": docs,
            "ground_truth": ground_truth,
        }

        final_score = 0
        for i in range(len(eval_result)):
            final_score += eval_result[
                i
            ]  # evaluate으로 평가하면 점수에 대한 reason도 반환하는데 그럼 eval_step을 입력해줘야함
            evaluation_result[Generation_criteria[i]["name"]] = (
                str(round(eval_result[i] * Generation_criteria[i]["weight"], 1)) + "점 "
            )

        evaluation_result["final_score"] = final_score

        return evaluation_result

    @traceable(run_type="G-eval")
    async def evaluate_batch(samples: list) -> list:
        results = []
        for item in samples:
            res = await evaluate_single_sample(
                question=item["question"], answer=item["docs"], ground_truth=item["ground_truth"]
            )
            results.append(res)

        with open("ret_evaluation_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        return results

    data = pd.read_csv(cfg.eval_data_path)

    samples = []

    for _, row in data.iterrows():
        sample = {
            "question": row["question"],
            "docs": [],
            "ground_truth": row["answer"],
        }
        sample["docs"] = retriever.get_relevant_documents(row["question"], k=cfg.tok_k)

        samples.append(sample)

    await evaluate_batch(samples)
