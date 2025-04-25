import logging
import sys
from pathlib import Path

from loguru import logger


def setup_logging():
    # 로그 파일 경로 설정
    log_path = Path("logs")
    log_path.mkdir(parents=True, exist_ok=True)

    # 로거 설정
    config = {
        "handlers": [
            {
                "sink": sys.stdout,
                "format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            },
            {
                "sink": log_path / "app.log",
                "rotation": "500 MB",
                "retention": "10 days",
                "format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
            },
        ],
    }

    # 기존 로거 제거
    logger.remove()

    # 새 설정 적용
    for handler in config["handlers"]:
        logger.add(**handler)

    # FastAPI 로거와 통합
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())
