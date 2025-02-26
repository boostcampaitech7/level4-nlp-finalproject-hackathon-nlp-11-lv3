from typing import List

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "RAG API Server"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # RAG 설정
    RAG_CONFIG_PATH: str = os.getenv("RAG_CONFIG_PATH", str(Path(__file__).parent.parent / "RAG/configs/config.yaml"))

    class Config:
        case_sensitive = True


settings = Settings()
