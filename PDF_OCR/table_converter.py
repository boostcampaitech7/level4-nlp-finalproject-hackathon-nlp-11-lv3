from typing import Dict, List, Union

import json
import os
from pathlib import Path
from bs4 import BeautifulSoup

import pandas as pd
import warnings
warnings.filterwarnings("ignore")


def json_to_table(json_data: Union[str, Dict]) -> pd.DataFrame:

    # JSON 데이터 로드
    if isinstance(json_data, str):
        with open(json_data, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = json_data

    try:
        html = data["content"]["html"]

        # beautifulsoup로 html 파싱
        soup = BeautifulSoup(html, 'html.parser')
        
        # html에서 테이블 추출
        df = pd.read_html(str(soup))[0]

        #csv 저장
        return df
        #print(f"처리 완료: {output_base} : {file}")
        

    except Exception as e:
        print(f"테이블 데이터 변환 중 오류 발생: {str(e)}")

def convert_json_to_csv(
    input_path: Union[str, Path], output_path: Union[str, Path] = None, recursive: bool = False
) -> None:
    """
    Args:
        input_path (Union[str, Path]): JSON 파일 또는 디렉토리 경로
        output_path (Union[str, Path], optional): 출력 경로.
            지정하지 않으면 입력 파일과 동일한 위치에 저장
        recursive (bool, optional): 디렉토리 처리시 하위 디렉토리도 처리할지 여부
    """
    input_path = Path(input_path)

    if output_path:
        output_path = Path(output_path)
        if not output_path.exists():
            output_path.mkdir(parents=True)

    def process_file(json_path: Path) -> None:
        try:
            # JSON 파일이 테이블 결과를 포함하는지 확인
            if not json_path.stem.endswith("_result"):
                return

            # 출력 경로 설정
            if output_path:
                csv_path = output_path / f"{json_path.stem.replace('_result', '')}.csv"
            else:
                csv_path = json_path.parent / f"{json_path.stem.replace('_result', '')}.csv"

            # 변환 및 저장
            table_df = json_to_table(str(json_path))
            table_df.to_csv(csv_path, encoding="utf-8-sig")
            print(f"변환 완료: {csv_path}")

        except Exception as e:
            print(f"파일 처리 중 오류 발생 ({json_path.name}): {str(e)}")

    # 단일 파일 처리
    if input_path.is_file():
        process_file(input_path)
        return

    # 디렉토리 처리
    if recursive:
        json_files = input_path.rglob("*.json")
    else:
        json_files = input_path.glob("*.json")

    for json_file in json_files:
        process_file(json_file)


                
        

def main():
    convert_json_to_csv("../../PDF_OCR/new_data/All_data/table.json")
if __name__ == "__main__":
    main() 