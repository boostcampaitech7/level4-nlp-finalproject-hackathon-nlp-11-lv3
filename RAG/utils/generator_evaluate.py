import asyncio
import json

from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams
from langsmith import Client, traceable

client = Client()
model = "gpt-4o-mini"
Generation_criteria = [
    {
        "name": "Relevance",
        "description": "Is the final answer clearly relevant to the question and reflective of the user’s intent?",
        "weight": 5,
    },
    {
        "name": "FactualCorrectness",
        "description": "Is the answer factually correct and free from unsupported or inaccurate information?",
        "weight": 5,
    },
    {
        "name": "Completeness",
        "description": (
            "Does the answer include all essential points " "required by the question and the ground_truth_answer?"
        ),
        "weight": 5,
    },
    {
        "name": "ClarityConciseness",
        "description": "Is the answer clear and concise, avoiding unnecessary repetition or ambiguity?",
        "weight": 5,
    },
    {
        "name": "LogicalStructure",
        "description": "Is the answer logically structured, consistent with the context, and free of contradictions?",
        "weight": 3,
    },
    {
        "name": "DetailwithoutExcessiveness",
        "description": "Does the answer provide sufficient detail for the question without being excessive?",
        "weight": 3,
    },
    {
        "name": "ProperCitation",
        "description": (
            "Does the answer provide proper citations or "
            "indications of the source when claims or data are referenced?"
        ),
        "weight": 2,
    },
    {
        "name": "Formatting",
        "description": "Is the answer presented in a suitable format (list, table, short text, etc.) for the question?",
        "weight": 1,
    },
    {
        "name": "ExtraInsights",
        "description": (
            "Does the answer offer any helpful extra insights or context "
            "that enrich the user’s understanding (without deviating from factual correctness)?"
        ),
        "weight": 1,
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
metric6 = GEval(
    name=Generation_criteria[5]["name"],
    criteria=Generation_criteria[5]["description"],
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
    model=model,
    threshold=0.0,
)
metric7 = GEval(
    name=Generation_criteria[6]["name"],
    criteria=Generation_criteria[6]["description"],
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
    model=model,
    threshold=0.0,
)
metric8 = GEval(
    name=Generation_criteria[7]["name"],
    criteria=Generation_criteria[7]["description"],
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
    model=model,
    threshold=0.0,
)
metric9 = GEval(
    name=Generation_criteria[8]["name"],
    criteria=Generation_criteria[8]["description"],
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
    model=model,
    threshold=0.0,
)


async def get_metric_evaluations(test_case: LLMTestCaseParams) -> list:
    return await asyncio.gather(
        metric1.evaluate(test_case),
        metric2.evaluate(test_case),
        metric3.evaluate(test_case),
        metric4.evaluate(test_case),
        metric5.evaluate(test_case),
        metric6.evaluate(test_case),
        metric7.evaluate(test_case),
        metric8.evaluate(test_case),
        metric9.evaluate(test_case),
    )


async def evaluate_single_sample(question: str, answer: str, ground_truth: str) -> dict:
    test_case = LLMTestCaseParams(input=question, actual_output=answer, expected_output=ground_truth)

    eval_result = await get_metric_evaluations(test_case)
    evaluation_result = {
        "question": question,
        "answer": answer,
        "ground_truth": ground_truth,
    }

    # deepeval에서는 0~10에서 score 매긴 후, 0~1로 매핑함
    final_score = 0
    for i in range(len(eval_result)):
        final_score += eval_result[i][0]
        evaluation_result[Generation_criteria[i]["name"]] = (
            eval_result[i][0] * Generation_criteria[i]["weight"] + "점 " + eval_result[i][1]
        )

    evaluation_result["final_score"] = final_score
    """
    client.log(
        run_type="evaluation",
        name="G-Eval Batch Evaluation",
        inputs={
            "question": evaluation_result["question"],
            "answer": evaluation_result["answer"],
            "ground_truth": evaluation_result["ground_truth"],
        },
        outputs={
            "final_score": result["final_score"],
            #criteria reasons
        },
    )
    """

    return evaluation_result


@traceable(run_type="G-eval")
def evaluate_batch(samples: list) -> list:
    results = []
    for item in samples:
        res = evaluate_single_sample(
            question=item["question"], answer=item["answer"], ground_truth=item["ground_truth"]
        )
        # asyncio.run(log_to_langsmith(res))
        results.append(res)

    with open("evaluation_results.json", "w", encoding="utf-8") as f:  # 추후 경로 수정
        json.dump(results, f, indent=2, ensure_ascii=False)

    return results
