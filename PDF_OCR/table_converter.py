from typing import Dict, List, Union

import json
from pathlib import Path

import pandas as pd


def json_to_table(json_data: Union[str, Dict]) -> pd.DataFrame:
    """
    OCR JSON 결과에서 테이블 데이터를 추출하여 DataFrame으로 변환합니다.

    Args:
        json_data (Union[str, Dict]): JSON 파일 경로 또는 JSON 데이터 딕셔너리

    Returns:
        pd.DataFrame: 변환된 테이블 데이터

    Raises:
        ValueError: 테이블 데이터를 찾을 수 없거나 변환 중 오류가 발생한 경우
    """
    # JSON 데이터 로드
    if isinstance(json_data, str):
        with open(json_data, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = json_data

    try:
        # 테이블 데이터 추출
        tables = data["images"][0]["tables"]
        table_rows = []

        for cell in tables[0]["cells"]:
            row_index = cell["rowIndex"]
            col_index = cell["columnIndex"]
            text = " ".join([line["cellWords"][0]["inferText"] for line in cell["cellTextLines"]])
            table_rows.append((row_index, col_index, text))

        # DataFrame 생성 및 피벗
        df = pd.DataFrame(table_rows, columns=["row", "col", "text"])
        pivot_table = df.pivot(index="row", columns="col", values="text")

        return pivot_table

    except Exception as e:
        raise ValueError(f"테이블 데이터 변환 중 오류 발생: {str(e)}")


def convert_json_to_csv(
    input_path: Union[str, Path], output_path: Union[str, Path] = None, recursive: bool = False
) -> None:
    """
    지정된 경로의 JSON 파일(들)을 CSV 파일로 변환합니다.

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


if __name__ == "__main__":

    # 1. 단일 JSON 파일을 CSV로 변환
    # convert_json_to_csv("path/to/table_result.json")

    # 2. 디렉토리 내 모든 JSON 파일을 CSV로 변환
    convert_json_to_csv("path/to/json/directory", "path/to/output/directory", recursive=True)
