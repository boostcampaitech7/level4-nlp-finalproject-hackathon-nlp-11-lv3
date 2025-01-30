import os
from pathlib import Path

# 프로젝트 루트 디렉토리 설정
PROJECT_ROOT = Path(__file__).parent  # .parent 제거하여 PDF_OCR 디렉토리를 루트로 설정

# 기본 설정값들
DEFAULT_CONFIG = {
    # 모델 관련 설정
    "MODEL": {
        "path": os.path.expanduser("~/.cache/huggingface/hub/models--juliozhao--DocLayout-YOLO-DocStructBench/snapshots/8c3299a30b8ff29a1503c4431b035b93220f7b11/doclayout_yolo_docstructbench_imgsz1024.pt"),
        #"path": "doclayout_yolo_docstructbench_imgsz1024.pt",  # 간단한 기본 경로
        "imgsz": 1024,
        "line_width": 5,
        "font_size": 20,
        "conf": 0.2,
        "threshold": 0.05,
    },
    
    # 디렉토리 설정
    "DIRS": {
        "input_dir": str(PROJECT_ROOT / "pdf"),  # PDF 파일이 있는 디렉토리
        "output_dir": str(PROJECT_ROOT / "output"),  # 중간 결과물 저장 디렉토리
        "database_dir": str(PROJECT_ROOT / "database"),  # 데이터베이스 저장 디렉토리
        "ocr_output_dir": str(PROJECT_ROOT / "ocr_results"),  # OCR 결과 저장 디렉토리
    },
    
    # 파일명 설정
    "FILES": {
        "database": "database.csv",
    },
}

def get_config(custom_config=None):
    """
    기본 설정값과 사용자 정의 설정값을 병합하여 반환
    
    Args:
        custom_config (dict, optional): 사용자 정의 설정값
    
    Returns:
        dict: 최종 설정값
    """
    config = DEFAULT_CONFIG.copy()
    
    if custom_config:
        # 중첩된 딕셔너리 업데이트
        for key, value in custom_config.items():
            if isinstance(value, dict) and key in config:
                config[key].update(value)
            else:
                config[key] = value
    
    # 디렉토리들 생성
    for dir_path in config["DIRS"].values():
        os.makedirs(dir_path, exist_ok=True)
    
    return config 