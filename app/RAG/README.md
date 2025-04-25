# RAG(실험) 사용 가이드

## 1. 환경 설정

### 1.1 환경 변수 설정
`.env` 파일을 설정합니다:
```bash
env로 openai API_Key, naverClova API_key 설정
```

# 2. 실험세팅(config 수정)

#### 매개변수 설명
- `passage_embedding_model_name` : vectorDB 만들 때 사용하는 embedding_model
- `query_embedding_model_name` : question embedding하는 모델
- `llm_model_name` : 생성형 모델
- `chat_template` : 프롬프트 템플릿


## 3. 실험

### 3.1 retrieve (평가)
```bash
cd RAG
python main.py mode=retrieve
```

### 3.2 generate (평가)
```bash
cd RAG
python main.py mode=generate
```

### 3.3 update_vectordb
```bash
cd RAG
python main.py mode=update_vectordb
```

## 4. 응답 형식

## 4.1 retriever G-eval(5가지 criteria, 총점 20)
```json
{
    "question": "question",
    "docs": "retrieved_docs",
    "ground_truth": "ground_truth",
    "criteria1": "criteria1_score",
    "criteria2": "criteria2_score",
    "final_score": "total_score"
}
```

## 4.2 generator G-eval(9가지 criteria, 총점 30)
```json
{
    "question": "question",
    "generated_answer": "generated_answer",
    "ground_truth": "ground_truth",
    "criteria1": "criteria1_score",
    "criteria2": "criteria2_score",
    "final_score": "total_score"
}
```