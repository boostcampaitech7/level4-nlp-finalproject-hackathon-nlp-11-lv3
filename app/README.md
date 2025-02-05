# RAG API 서버 사용 가이드

## 1. 환경 설정

### 1.1 환경 변수 설정
`.env` 파일을 설정합니다:
```bash

```

### 1.2 의존성 설치
```bash
pip install -r app/requirements.txt
```

## 2. 서버 실행

### 2.1 개발 모드
```bash
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2.2 API 서버 모드
```bash
cd app
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## 3. API 엔드포인트

### 3.1 질문하기 (POST `/api/v1/query`)

#### 요청 형식
```json
{
    "query": "질문 내용",
    "max_tokens": 256,
    "temperature": 0.7
}
```

#### 매개변수 설명
- `query` (필수): 사용자의 질문
- `max_tokens` (선택, 기본값: 256): 생성할 최대 토큰 수
- `temperature` (선택, 기본값: 0.7): 생성 텍스트의 다양성 (0.0 ~ 1.0)

#### 응답 형식
```json
{
    "answer": "생성된 답변",
    "retrieved_documents": [
        {
            "content": "검색된 문서 내용",
            "score": 0.95,
            "source": "문서 출처",
            "company": "카카오뱅크"
        }
    ],
    "processing_time": 1.23,
    "company": "카카오뱅크"
}
```

### 3.2 API 호출 예시

#### cURL
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
     -H "Content-Type: application/json" \
     -d '{
         "query": "카카오뱅크의 2024년 매출액은?",
         "max_tokens": 1000,
         "temperature": 0.7
     }'
```

#### Python
```python
import requests

url = "http://localhost:8000/api/v1/query"
data = {
    "query": "질문 내용",
    "max_tokens": 1000,
    "temperature": 0.7
}

response = requests.post(url, json=data)
result = response.json()
print(result["answer"])
```

## 4. 모니터링

### 4.1 메트릭스
- Prometheus 메트릭스: `http://localhost:8000/metrics`

### 4.2 로그
- 로그 파일 위치: `app/logs/app.log`
- 로그 레벨 설정: `.env` 파일의 `LOG_LEVEL` 변수로 조정

## 5. 문제 해결

### 5.1 일반적인 오류
- 500 에러: 서버 내부 오류, 로그 파일 확인
- 404 에러: 잘못된 엔드포인트 접근
- 422 에러: 잘못된 요청 형식

### 5.2 로그 확인
```bash
tail -f app/logs/app.log
``` 