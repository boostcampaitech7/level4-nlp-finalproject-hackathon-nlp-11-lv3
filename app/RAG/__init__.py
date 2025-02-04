"""
RAG (Retrieval Augmented Generation) 패키지
"""

import sys
from pathlib import Path

# 패키지 루트 경로
ROOT_PATH = Path(__file__).parent.absolute()

# Python 경로에 RAG 루트 추가
if str(ROOT_PATH) not in sys.path:
    sys.path.append(str(ROOT_PATH))

# 데이터 경로
DATA_PATH = ROOT_PATH / "data"
VECTOR_STORE_PATH = ROOT_PATH / "vector_store"

# 설정 파일 경로
CONFIG_PATH = ROOT_PATH / "configs"
