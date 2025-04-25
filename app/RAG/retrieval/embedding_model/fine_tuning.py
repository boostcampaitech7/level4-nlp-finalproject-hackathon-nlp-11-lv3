from typing import Dict, List, Tuple

import gc
import os

import pandas as pd
import torch
import torch.nn.functional as F
import wandb
from sentence_transformers import SentenceTransformer
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader
from tqdm import tqdm
from torch.optim import AdamW
from transformers import get_scheduler

# 환경 설정
WANDB_PROJECT = "retriever_embedding_model_fine-tuning"
MODEL_NAME = "nlpai-lab/KoE5"
EPOCHS = 10
LR = 0.00007180661859592403  # USE_SWEEP=True면 무시
WARMUP_RATIO = 0.1
BATCH_SIZE = 24
ACCUMULATION_STEPS = 64  # USE_SWEEP=True면 무시
TEMPERATURE = 0.04184381288580703  # USE_SWEEP=True면 무시
SAVE_INTERVAL = 3  # 몇 epoch마다 저장할지 (Sweep 사용 안할 때만)
EARLY_STOPPING_PATIENCE = 3
USE_SWEEP = False  # Sweep 사용 여부 설정
COUNT = 30
CSV_PATH = "/data/ephemeral/home/data/fine-tuning_data.csv"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

if USE_SWEEP:
    # WandB Sweep 설정
    sweep_config = {
        "method": "bayes",
        "metric": {"name": "eval_loss", "goal": "minimize"},
        "parameters": {
            "learning_rate": {"distribution": "log_uniform_values", "min": 1e-7, "max": 5e-4},
            "temperature": {"distribution": "uniform", "min": 0.01, "max": 0.1999},
            "accumulation_steps": {"values": [4, 8, 16, 32, 64]},
        },
    }
    sweep_id = wandb.sweep(sweep_config, project=WANDB_PROJECT)

df = pd.read_csv(CSV_PATH)

# 데이터 Train / Eval 분할
train_samples, eval_samples = train_test_split(list(zip(df["question"], df["context"])), test_size=0.2, random_state=42)


# DataLoader 설정
def dual_collate(batch: List[Tuple[str, str]]) -> Dict[str, List[str]]:
    """
    데이터 Collate 함수: 배치 데이터를 Query와 Passage로 분리하여 반환

    Args:
        batch (List[Tuple[str, str]]): (query, passage) 데이터 샘플

    Returns:
        Dict[str, List[str]]: {'queries': Query 리스트, 'passages': Passage 리스트}
    """
    queries, passages = zip(*batch)
    return {"queries": [q for q in queries], "passages": [p for p in passages]}


train_dataloader = DataLoader(train_samples, batch_size=BATCH_SIZE, shuffle=True, collate_fn=dual_collate)
eval_dataloader = DataLoader(eval_samples, batch_size=BATCH_SIZE, shuffle=False, collate_fn=dual_collate)


def encode_with_grad(model: SentenceTransformer, texts: List[str]) -> torch.Tensor:
    """
    주어진 문장을 SentenceTransformer 모델을 사용하여 임베딩 변환

    Args:
        model (SentenceTransformer): 임베딩을 생성할 모델
        texts (List[str]): 입력 텍스트 리스트

    Returns:
        torch.Tensor: 문장 임베딩
    """
    features = model.tokenizer(texts, padding=True, truncation=True, return_tensors="pt", max_length=120)
    features = {k: v.to(device) for k, v in features.items()}  # GPU로 이동
    outputs = model.forward(features)
    return outputs["sentence_embedding"]


def multiple_negatives_ranking_loss(
    query_embeds: torch.Tensor, passage_embeds: torch.Tensor, temperature: float
) -> torch.Tensor:
    """
    Multiple Negatives Ranking Loss 계산

    Args:
        query_embeds (torch.Tensor): Query 임베딩 텐서
        passage_embeds (torch.Tensor): Passage 임베딩 텐서
        temperature (float): Softmax 스케일링 값

    Returns:
        torch.Tensor: 계산된 Loss 값
    """
    scores = torch.matmul(query_embeds, passage_embeds.T) / temperature
    log_probs = F.log_softmax(scores, dim=1)
    labels = torch.arange(scores.shape[0]).to(device)
    return F.nll_loss(log_probs, labels)


def evaluate(
    query_encoder: SentenceTransformer, passage_encoder: SentenceTransformer, dataloader: DataLoader, temperature: float
) -> float:
    """
    모델 평가 함수

    Args:
        query_encoder (SentenceTransformer): Query 인코더 모델
        passage_encoder (SentenceTransformer): Passage 인코더 모델
        dataloader (DataLoader): 평가 데이터 로더
        temperature (float): Loss 계산에 사용할 온도 값

    Returns:
        float: 평가 데이터의 평균 Loss 값
    """
    query_encoder.eval()
    passage_encoder.eval()
    total_loss = 0.0

    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Evaluating"):
            query_embeds = encode_with_grad(query_encoder, batch["queries"])
            passage_embeds = encode_with_grad(passage_encoder, batch["passages"])
            loss = multiple_negatives_ranking_loss(query_embeds, passage_embeds, temperature)
            total_loss += loss.item()

    avg_loss = total_loss / len(dataloader)
    return avg_loss


def train() -> None:
    """
    모델 학습 함수: WandB Sweep 또는 수동 설정을 기반으로 학습 수행
    """
    lr = LR
    tempurature = TEMPERATURE
    accumulation_steps = ACCUMULATION_STEPS

    wandb.init(
        project=WANDB_PROJECT,
        config={
            "batch_size": BATCH_SIZE,
            "epochs": EPOCHS,
            "learning_rate": LR,
            "temperature": TEMPERATURE,
            "accumulation_steps": ACCUMULATION_STEPS,
        },
    )

    if USE_SWEEP:
        print(f"현재 Sweep 실행: {wandb.run.name} (ID: {wandb.run.id})")
        sweep_run_number = len(list(wandb.Api().runs(WANDB_PROJECT)))
        print(f"현재 Sweep 실행 횟수: {sweep_run_number}")
        lr = wandb.config.learning_rate
        tempurature = wandb.config.temperature
        accumulation_steps = wandb.config.accumulation_steps

    query_encoder = SentenceTransformer(MODEL_NAME).to(device)
    passage_encoder = SentenceTransformer(MODEL_NAME).to(device)
    optimizer = AdamW(list(query_encoder.parameters()) + list(passage_encoder.parameters()), lr=lr)
    total_steps = len(train_dataloader) * EPOCHS // accumulation_steps
    warmup_steps = int(WARMUP_RATIO * total_steps)
    lr_scheduler = get_scheduler(
        "linear", optimizer=optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_steps
    )

    best_eval_loss = float("inf")
    patience_counter = 0
    early_stopping_patience = EARLY_STOPPING_PATIENCE

    for epoch in range(1, EPOCHS + 1):
        total_loss = 0.0
        query_encoder.train()
        passage_encoder.train()
        optimizer.zero_grad()

        loop = tqdm(train_dataloader, desc=f"Epoch {epoch}")

        for step, batch in enumerate(loop):
            query_embeds = encode_with_grad(query_encoder, batch["queries"])
            passage_embeds = encode_with_grad(passage_encoder, batch["passages"])
            loss = multiple_negatives_ranking_loss(query_embeds, passage_embeds, tempurature)
            loss = loss / accumulation_steps
            loss.backward()

            if (step + 1) % accumulation_steps == 0 or (step + 1 == len(train_dataloader)):
                optimizer.step()
                lr_scheduler.step()
                optimizer.zero_grad()
                torch.cuda.empty_cache()
            total_loss += loss.item() * accumulation_steps
            loop.set_postfix(loss=loss.item() * accumulation_steps)  # 출력은 원래 loss 값
            wandb.log({"step_loss": loss.item() * accumulation_steps, "learning_rate": lr_scheduler.get_last_lr()[0]})

        avg_train_loss = total_loss / len(train_dataloader)
        eval_loss = evaluate(query_encoder, passage_encoder, eval_dataloader, tempurature)
        print(f"Epoch {epoch} | Train_Loss: {avg_train_loss:.4f} | Eval_Loss: {eval_loss:.4f}")
        wandb.log({"epoch": epoch, "train_loss": avg_train_loss, "eval_loss": eval_loss})

        if not USE_SWEEP and (epoch % SAVE_INTERVAL == 0 or epoch == EPOCHS):
            save_dir = f"epoch{epoch}"
            os.makedirs(save_dir, exist_ok=True)
            query_encoder.save(f"{save_dir}/query_encoder")
            passage_encoder.save(f"{save_dir}/passage_encoder")
            print(f"모델 저장 완료: {save_dir}/")

        if eval_loss < best_eval_loss:
            best_eval_loss = eval_loss
            patience_counter = 0
        else:
            patience_counter += 1

        if patience_counter >= early_stopping_patience:
            print(f"Early stopping at epoch {epoch}")
            break

    # 모델 삭제
    del query_encoder
    del passage_encoder

    # Python 가비지 컬렉션 실행
    gc.collect()

    # CUDA 메모리 정리
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()


if USE_SWEEP:
    wandb.agent(sweep_id, train, count=COUNT)
else:
    train()
