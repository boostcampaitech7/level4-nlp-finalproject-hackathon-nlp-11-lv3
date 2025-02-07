import json
import os
import time
import uuid

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()


def process_image_ocr(image_file, is_table=False):
    """
    이미지 파일에 대해 OCR을 수행하는 함수

    Args:
        image_file (str): OCR을 수행할 이미지 파일 경로

    Returns:
        dict: OCR 결과
    """
    api_url = os.getenv("clova_api_url")
    secret_key = os.getenv("clova_secret_key")
    """
    naver clova ocr api 사용
    version : model version
    requestId : 요청 고유 식별자
    timestamp : 요청 시간
    enableTableDetection: 테이블 여부
    """
    request_json = {
        "images": [{"format": "png", "name": "demo"}],
        "requestId": str(uuid.uuid4()),
        "version": "V2",
        "timestamp": int(round(time.time() * 1000)),
        "enableTableDetection": is_table,
    }

    payload = {"message": json.dumps(request_json).encode("UTF-8")}

    with open(image_file, "rb") as f:
        files = [("file", f)]
        headers = {"X-OCR-SECRET": secret_key}
        response = requests.request("POST", api_url, headers=headers, data=payload, files=files)

    return response.json()
