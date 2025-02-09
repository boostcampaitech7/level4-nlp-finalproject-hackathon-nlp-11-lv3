import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import hydra
from dotenv import load_dotenv
from omegaconf import DictConfig

# from source.finetune_ret import finetune
# from source.generate import generate
# from source.retrieve import retrieve
from utils.vector_store import VectorStore


@hydra.main(version_base="1.3", config_path="configs", config_name="config")
def main(cfg: DictConfig):
    print(sys.path)
    load_dotenv()
    cfg.openai_key = os.getenv("OPENAI_API_KEY")

    if cfg.mode == "retrieve":
        print("test retrieval")
        # retrieve(cfg)

    elif cfg.mode == "generate":
        print("test inference")
        # generate(cfg)

    elif cfg.mode == "update_vectordb":
        print("벡터 DB 업데이트 시작")

        # 디렉토리 설정
        vector_db_dir = "vector_db"
        old_data_dir = "old_data"

        if not os.path.exists(vector_db_dir):
            os.makedirs(vector_db_dir)
        if not os.path.exists(old_data_dir):
            os.makedirs(old_data_dir)

        # JSON 파일 경로 설정
        text_json_path = "../../PDF_OCR/new_data/All_data/text.json"
        table_json_path = "../../PDF_OCR/new_data/All_data/table.json"

        # 파일이 존재하는지 확인
        if not (os.path.exists(text_json_path) and os.path.exists(table_json_path)):
            print("새로운 데이터 파일이 없습니다.")
            return

        try:
            # 벡터 스토어 초기화 및 업데이트
            vector_store = VectorStore(cfg=cfg, persist_directory=vector_db_dir)
            # vector_store.update_company_vector_stores(text_json_path, table_json_path)
            vector_store.update_all_vector_stores(text_json_path, table_json_path)
            # 처리된 파일 이동
            vector_store.move_to_old_data(
                [text_json_path, table_json_path], old_data_dir="../../PDF_OCR/old_data", user_name="All_data"
            )
            print("벡터 DB 업데이트 완료")

        except Exception as e:
            print(f"오류 발생: {str(e)}")


if __name__ == "__main__":
    main()
