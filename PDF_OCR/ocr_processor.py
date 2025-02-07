import json
import os

import pandas as pd
from ocr_api import process_image_ocr
from table_converter import json_to_table


class OCRProcessor:
    def __init__(self, base_folder="pdf", output_folder="./ocr_results"):
        self.base_folder = base_folder
        self.output_folder = output_folder

        # 결과 저장할 폴더 생성
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def process_folders(self):
        # PDF 파일명으로 생성된 폴더 순회
        for pdf_folder in os.listdir(self.base_folder):
            pdf_path = os.path.join(self.base_folder, pdf_folder)
            if not os.path.isdir(pdf_path):
                continue

            # PDF별 결과 폴더 생성
            pdf_output = os.path.join(self.output_folder, pdf_folder)
            if not os.path.exists(pdf_output):
                os.makedirs(pdf_output)

            # images 폴더 경로
            images_path = os.path.join(pdf_path, "images")
            if not os.path.exists(images_path):
                continue

            # 페이지별 폴더 순회
            for page in os.listdir(images_path):
                page_path = os.path.join(images_path, page)
                if not os.path.isdir(page_path):
                    continue

                # split_images 폴더 경로
                split_images_path = os.path.join(page_path, "split_images")
                if not os.path.exists(split_images_path):
                    continue

                # 페이지별 결과 폴더 생성
                page_output = os.path.join(pdf_output, page)
                if not os.path.exists(page_output):
                    os.makedirs(page_output)

                # 이미지 파일 처리
                self.process_image_files(split_images_path, page_output)

    def process_image_files(self, input_path, output_path):
        for file in os.listdir(input_path):
            # plain text나 table이 포함된 파일만 처리
            if not ("plain text" in file.lower() or "table" in file.lower()):
                continue
            # 테이블 파일만 처리
            if "table" in file.lower():
                if "caption" in file.lower() or "footnote" in file.lower() or "caption" in file.lower():
                    continue
            if not file.lower().endswith((".png", ".jpg", ".jpeg")):
                continue

            input_file = os.path.join(input_path, file)
            output_base = os.path.join(output_path, os.path.splitext(file)[0])

            try:
                # 결과가 테이블인 경우
                if "table" in file.lower():
                    result = process_image_ocr(input_file, is_table=True)
                    # JSON 결과 저장
                    json_path = f"{output_base}_result.json"
                    with open(json_path, "w", encoding="utf-8") as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)

                    # 테이블 데이터 추출 및 CSV 저장
                    try:
                        table_df = json_to_table(result)
                        table_df.to_csv(f"{output_base}.csv", encoding="utf-8-sig")
                    except Exception as e:
                        print(f"테이블 처리 중 오류 발생 ({file}): {str(e)}")

                # 일반 텍스트인 경우
                else:
                    result = process_image_ocr(input_file, is_table=False)
                    # JSON 결과만 저장
                    with open(f"{output_base}_result.json", "w", encoding="utf-8") as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)

                print(f"처리 완료: {file}")

            except Exception as e:
                print(f"파일 처리 중 오류 발생 ({file}): {str(e)}")


def main():
    processor = OCRProcessor()
    processor.process_folders()


if __name__ == "__main__":
    main()
