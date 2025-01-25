from typing import Any, Callable, Dict, List, Tuple

import os
import re
import shutil
from collections import defaultdict
from functools import cmp_to_key

import cv2
import numpy as np
import pandas as pd
import torch
from doclayout_yolo import YOLOv10
from pdf2image import convert_from_path
from tqdm import tqdm


def pdf_to_image(pdf_path: str, save_path: str, db_path: str, verbose: bool = False) -> None:
    """
    주어진 PDF 파일을 이미지로 변환하고, PDF 파일을 지정된 디렉토리로 이동하며, 변환된 이미지를 저장합니다.
    또한 변환한 정보를 `database.csv` 파일에 기록합니다.

    Args:
        pdf_path (str): 변환할 PDF 파일의 경로.
        save_path (str): 변환된 이미지와 PDF 파일을 저장할 폴더 경로.
        db_path (str): 데이터베이스 경로
        verbose (bool, optional): 이미지 저장 진행 상황을 출력할지 여부 (기본값은 False).

    Returns:
        None: 함수는 반환값이 없습니다.
    """

    # 종목 이름
    company_name = os.path.basename(save_path)

    # PDF 파일 이름을 기반으로 폴더 이름 생성 (확장자 제외)
    file_name = os.path.splitext(os.path.basename(pdf_path))[0]

    # 폴더 경로 생성
    output_dir = os.path.join(save_path, file_name)  # 현재 작업 디렉토리 내에 생성
    os.makedirs(output_dir, exist_ok=True)

    # PDF 파일 이동
    new_pdf_path = os.path.join(output_dir, os.path.basename(pdf_path))
    shutil.move(pdf_path, new_pdf_path)

    # images 저장 폴더 생성
    output_dir = os.path.join(output_dir, "images")  # 현재 작업 디렉토리 내에 생성
    os.makedirs(output_dir, exist_ok=True)

    # PDF를 이미지로 변환
    images = convert_from_path(new_pdf_path, dpi=300)

    # PDF 페이지 수
    num_pages = len(images)

    # 각 페이지를 이미지로 저장
    for page_num, image in enumerate(images, start=1):
        # 이미지 파일명 설정
        output_image_path = os.path.join(output_dir, f"page_{page_num}.png")

        # 이미지 저장
        image.save(output_image_path, "PNG")
        if verbose:
            print(f"Page {page_num} saved as {output_image_path}")

    # 파일에 대한 메타 데이터 기록
    new_data = pd.DataFrame(
        {
            "company_name": [company_name] * num_pages,
            "file_name": [file_name] * num_pages,
            "page": [i for i in range(1, num_pages + 1)],
        }
    )

    # 데이터베이스 업데이트
    if os.path.exists(db_path):
        database = pd.read_csv(db_path, encoding="utf-8")
    else:
        database = pd.DataFrame(columns=["company_name", "file_name", "page"])

    # concat으로 두 DataFrame을 병합
    database = pd.concat([database, new_data], ignore_index=True)

    # 'page' 열을 정수형으로 변환
    database["page"] = database["page"].astype("int")

    # company_name -> file_name -> page 순으로 오름차순 정렬
    database = database.sort_values(by=["company_name", "file_name", "page"], ascending=[True, True, True])

    # database csv로 저장
    database.to_csv(db_path, index=False, encoding="utf-8")


def multi_pdf_to_image(root_dir: str, db_path: str) -> None:
    """
    주어진 루트 디렉토리 내 모든 하위 디렉토리에서 PDF 파일을 찾아 변환하는 함수입니다.
    각 PDF 파일은 `pdf_to_image` 함수로 처리되어 이미지로 변환됩니다.

    Args:
        root_dir (str): PDF 파일이 저장된 루트 디렉토리 경로.
        db_path (str): 데이터베이스 경로

    Returns:
        None: 함수는 반환값이 없습니다.
    """

    # 루트 디렉토리 내 모든 하위 디렉토리와 파일을 순회
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            # PDF 파일만 처리
            if filename.lower().endswith(".pdf"):
                pdf_path = os.path.join(dirpath, filename)
                print(f"Converting {pdf_path} to images...")

                # 동일한 디렉토리 구조를 유지하며 이미지 저장
                pdf_to_image(pdf_path, dirpath, db_path=db_path, verbose=False)


def sort_bounding_boxes(output_data, image_width):
    def get_columns(data, image_width, threshold_x=0.085, threshold_diff=1, threshold_column=0.1):
        """
        Group bounding boxes into columns based on their x_min values.
        """
        # 데이터를 정렬
        x_mins = np.array([item["coordinates"][0] for item in data])
        sorted_x = np.sort(x_mins)

        # 그룹을 저장할 리스트
        grouped = []

        # 첫 번째 값을 시작으로 그룹 초기화
        current_group = [sorted_x[0]]

        # 정렬된 데이터를 순회
        for i in range(1, len(sorted_x)):
            if abs(sorted_x[i] - current_group[-1]) <= image_width * threshold_x:
                # threshold 이내의 값은 같은 그룹으로 추가
                current_group.append(sorted_x[i])
            else:
                # 그룹을 저장하고 새 그룹 시작
                grouped.append(current_group)
                current_group = [sorted_x[i]]

        # 마지막 그룹 추가
        grouped.append(current_group)

        grouped_count = list(map(len, grouped))
        # 1. grouped_count의 오름차순 정렬 (원래 인덱스 추적)
        sorted_indices = np.argsort(grouped_count)  # 정렬된 인덱스
        sorted_grouped_count = [grouped_count[i] for i in sorted_indices]  # 정렬된 grouped_count

        # 2. diff 계산
        diffs = np.diff(sorted_grouped_count)

        # 3. diff가 특정 임계값 이상으로 증가한 지점 찾기
        sudden_increase_indices = np.where(diffs >= threshold_diff)[0] + 1  # +1은 diff의 결과가 n-1 길이이기 때문

        if len(sudden_increase_indices) != 0:
            # 4. 갑작스러운 변화 이후의 원래 인덱스 찾기
            original_indices = sorted_indices[sudden_increase_indices[0] :]
            mode_components_list = [grouped[i] for i in original_indices]
            x_column_boundary = [min(mode_components) for mode_components in mode_components_list]
            x_column_boundary.sort()
            column_bounds = [(0, x_column_boundary[0])]
            for i in range(len(x_column_boundary) - 1):
                column_bounds.append((x_column_boundary[i], x_column_boundary[i + 1]))
            column_bounds.append((x_column_boundary[-1], float("inf")))
        else:  # 다단은 나누어져 있는데 다단 자체가 바운딩 박스 하나로 크게 이루어져있으면
            # 최빈값이 1로 동률일 경우 x_min 좌표 사이 간격을 분석해서 좌표 사이 간격이 갑자기 커지는 곳을 다단으로 인식하게 한다.
            gaps = np.diff(sorted_x)
            column_threshold = threshold_column * (sorted_x[-1] - sorted_x[0])
            column_indices = np.where(gaps > column_threshold)[0]

            columns = []
            start = 0
            for idx in column_indices:
                columns.append(sorted_x[start : idx + 1])
                start = idx + 1
            columns.append(sorted_x[start:])

            column_bounds = [[col.min(), col.max()] for col in map(np.array, columns)]
            column_bounds.insert(0, (0, column_bounds[0][0]))
            for i in range(1, len(column_bounds) - 1):
                column_bounds[i][1] = column_bounds[i + 1][0]
            column_bounds.append((column_bounds[-1][1], float("inf")))
        return column_bounds

    def assign_column(box, column_bounds):
        """Assign a bounding box to its column."""
        x_min = box["coordinates"][0]  # bounding box의 x_min 값을 가져옴
        for idx, (col_min, col_max) in enumerate(column_bounds):  # 각 컬럼의 경계 확인
            if col_min <= x_min < col_max:  # x_min이 컬럼 경계 안에 있으면
                return idx  # 해당 컬럼의 인덱스를 반환
        return len(column_bounds)  # 컬럼 경계에 속하지 않으면 마지막 인덱스를 반환

    def fuzzy_comparator(box1, box2):
        # 두 박스의 x_min, y_min 좌표 추출
        x1, y1, _, _ = box1["coordinates"]
        x2, y2, _, _ = box2["coordinates"]

        y_threshold = 32

        # y좌표가 비슷하면 x좌표 기준으로 비교
        if abs(y1 - y2) <= y_threshold:
            return x1 - x2
        # 그렇지 않으면 y좌표 기준으로 비교
        return y1 - y2

    def sort_within_column(boxes):
        """Sort boxes within a column by y_min, then x_min."""
        return sorted(boxes, key=cmp_to_key(fuzzy_comparator))
        # return sorted(boxes, key=lambda b: (b['coordinates'][1], b['coordinates'][0]))

    # Step 1: Detect columns based on x_min values
    column_bounds = get_columns(output_data, image_width)
    if not column_bounds:
        tolerance = 0.05
        sorted_boxes = sorted(
            output_data, key=lambda b: ((b["coordinates"][1] // tolerance) * tolerance, b["coordinates"][0])
        )
        return sorted_boxes
    else:
        column_data = defaultdict(list)

        for box in output_data:
            column_idx = assign_column(box, column_bounds)
            column_data[column_idx].append(box)

        # Step 2: Sort columns based on width (wide to narrow or left to right if similar)
        sorted_columns = sorted(
            column_data.items(),
            key=lambda c: (
                -(max(box["coordinates"][2] for box in c[1]) - min(box["coordinates"][0] for box in c[1])),
                c[0],
            ),
        )

        # Step 3: Sort boxes within each column
        sorted_boxes = []
        for _, boxes in sorted_columns:
            sorted_boxes.extend(sort_within_column(boxes))

        return sorted_boxes


def extract_and_save_bounding_boxes(
    image_path,
    database_path,
    model_path="/data/ephemeral/home/.cache/huggingface/hub/models--juliozhao--DocLayout-YOLO-DocStructBench/snapshots/8c3299a30b8ff29a1503c4431b035b93220f7b11/doclayout_yolo_docstructbench_imgsz1024.pt",
    res_path="outputs",
    imgsz=1024,
    line_width=5,
    font_size=20,
    conf=0.2,
    split_images_foler_name="split_images",
    threshold=0.05,
    verbose=False,
):

    # Automatically select device
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

    model = YOLOv10(model_path)  # load an official model

    det_res = model.predict(
        image_path,
        imgsz=imgsz,
        conf=conf,
        device=device,
    )
    annotated_frame = det_res[0].plot(pil=True, line_width=line_width, font_size=font_size)
    if not os.path.exists(res_path):
        os.makedirs(res_path)
    output_path = os.path.join(res_path, image_path.split("/")[-1].replace(".png", "_annotated.png"))
    cv2.imwrite(output_path, annotated_frame)
    print(f'The result was saved to "{output_path}"')

    # 클래스 ID와 이름 매핑
    CLASS_LABELS = {
        0: "title",
        1: "plain text",
        2: "abandon",
        3: "figure",
        4: "figure_caption",
        5: "table",
        6: "table_caption",
        7: "table_footnote",
        8: "isolate_formula",
        9: "formula_caption",
    }

    image = cv2.imread(image_path)

    # 결과 저장 디렉토리 생성
    output_dir = os.path.join(res_path, f"{split_images_foler_name}")
    print(f'Split images were saved to "{output_dir}"')
    os.makedirs(output_dir, exist_ok=True)

    # 클래스별 고유 인덱스 관리
    class_indices = defaultdict(int)  # 각 클래스별 저장 인덱스

    output_data = []
    unique_boxes = {}  # 중복된 박스를 방지하고 최고 확률로 저장하기 위한 딕셔너리

    for box in det_res[0].boxes.data:
        # Bounding Box 정보 추출
        x_min, y_min, x_max, y_max = map(int, box[:4].cpu().numpy())  # 좌표
        confidence = box[4].cpu().numpy()  # 신뢰도 점수
        class_id = int(box[5].cpu().numpy())  # 클래스 ID
        class_name = CLASS_LABELS.get(class_id, "Unknown")  # 클래스 이름 매핑

        # 좌표를 기준으로 중복 체크 및 최고 확률 유지
        box_tuple = (x_min, y_min, x_max, y_max)

        # 중복 박스를 체크
        overlap_found = False
        for existing_key, existing_box in list(unique_boxes.items()):
            existing_coordinates = existing_box["coordinates"]

            x_min1, y_min1, x_max1, y_max1 = x_min, y_min, x_max, y_max
            x_min2, y_min2, x_max2, y_max2 = existing_coordinates

            # 교집합 영역의 좌표 계산
            x_min_inter = max(x_min1, x_min2)
            y_min_inter = max(y_min1, y_min2)
            x_max_inter = min(x_max1, x_max2)
            y_max_inter = min(y_max1, y_max2)

            # 교집합 면적
            if x_max_inter - x_min_inter > 0 and y_max_inter - y_min_inter > 0:
                intersection_area = (x_max_inter - x_min_inter) * (y_max_inter - y_min_inter)
            else:
                intersection_area = 0

            # 두 박스의 면적 계산
            area1 = (x_max1 - x_min1) * (y_max1 - y_min1)
            area2 = (x_max2 - x_min2) * (y_max2 - y_min2)

            if area1 - intersection_area < threshold * area1 and area2 - intersection_area < threshold * area2:
                # 두 박스가 거의 일치하면, 확률이 더 높은 박스로 교체
                if confidence > existing_box["confidence"]:
                    del unique_boxes[existing_key]
                    if box_tuple not in unique_boxes.keys():
                        unique_boxes[box_tuple] = {
                            "class_name": class_name,
                            "confidence": confidence,
                            "coordinates": [x_min, y_min, x_max, y_max],
                        }
                overlap_found = True
            elif area1 < area2 and area1 - intersection_area < threshold * area1:
                # 현재 박스가 더 작은 경우, 기존 박스를 제거
                del unique_boxes[existing_key]
                unique_boxes[box_tuple] = {
                    "class_name": class_name,
                    "confidence": confidence,
                    "coordinates": [x_min, y_min, x_max, y_max],
                }
                overlap_found = True
            elif area2 < area1 and area2 - intersection_area < threshold * area2:
                # 기존 박스가 더 작은 경우, 현재 박스를 추가하지 않음
                overlap_found = True

        # 중복이 없으면 새로운 박스를 추가
        if not overlap_found:
            unique_boxes[box_tuple] = {
                "class_name": class_name,
                "confidence": confidence,
                "coordinates": [x_min, y_min, x_max, y_max],
            }

    print("num_split_images: {num_split_images}".format(num_split_images=len(unique_boxes)))

    # 결과 저장 및 이미지 자르기
    for _, box_info in unique_boxes.items():
        x_min, y_min, x_max, y_max = box_info["coordinates"]
        class_name = box_info["class_name"]
        confidence = box_info["confidence"]

        # 클래스별 고유 인덱스 추가
        class_index = class_indices[class_name] + 1
        class_indices[class_name] += 1

        # 정보 저장
        output_data.append(
            {
                "box_id": class_index,
                "class_name": class_name,
                "confidence": float(confidence),
                "coordinates": [x_min, y_min, x_max, y_max],
            }
        )

    # 메타 데이터 생성
    dir_path = os.path.dirname(image_path)
    path_parts = dir_path.split("/")
    company_name = path_parts[-3]
    file_name = path_parts[-2]
    page = os.path.splitext(os.path.basename(image_path))[0]
    page = int(page.split("_")[-1])

    # ouput_data를 다단을 따라 위에서 아래로 읽고 다른 다단을 위에서 아래로 읽는 순서로 정렬
    output_data = sort_bounding_boxes(output_data, image.shape[1])

    # 저장된 데이터 확인
    if verbose:
        for data in output_data:
            print(data)

    # 파일에 대한 메타 데이터 기록
    num_page_components = len(unique_boxes)
    new_data = pd.DataFrame(
        {
            "company_name": [company_name] * num_page_components,
            "file_name": [file_name] * num_page_components,
            "page": [page] * num_page_components,
            "component_index": [i for i in range(1, len(output_data) + 1)],
            "component_type": [component["class_name"] for component in output_data],
            "component_type_sub_index": [component["box_id"] for component in output_data],
            "coordinates-x_min,y_min,x_max,y_max": [
                component["coordinates"] for component in output_data
            ],  # left, top, right, bottom
            "component_type_confidence": [component["confidence"] for component in output_data],
        }
    )

    # 각 component_type에 대해 별도로 'box_id' 매기기
    new_data["component_type_sub_index"] = new_data.groupby("component_type").cumcount() + 1
    new_data["component_index"] = range(1, len(new_data) + 1)

    for _, row in new_data.iterrows():
        # 박스 영역 잘라내기
        x_min, y_min, x_max, y_max = row["coordinates-x_min,y_min,x_max,y_max"]
        cropped_image = image[y_min:y_max, x_min:x_max]

        # 잘라낸 이미지 저장
        cropped_image_path = os.path.join(
            output_dir, f"{row['component_index']}_{row['component_type']}_{row['component_type_sub_index']}.png"
        )
        cv2.imwrite(cropped_image_path, cropped_image)
    database = pd.read_csv(database_path, encoding="utf-8")

    # 조건에 맞는 행 인덱스를 찾기
    matching_indices = database.loc[
        (database["company_name"] == company_name) & (database["file_name"] == file_name) & (database["page"] == page)
    ].index
    matching_indices = matching_indices[0]

    # 기존 DataFrame에서 현재 입력 이미지의 company_name, file_name, page에 대응하는 행을 삭제하고 new_data를 삽입하는 방식으로
    # 문서 페이지 이미지가 여러 components로 나누어졌으므로 components에 대응하는 여러 행으로 기존 하나의 행을 교체
    database = pd.concat(
        [database.iloc[:matching_indices], new_data, database.iloc[matching_indices + 1 :]]
    ).reset_index(drop=True)

    # database csv로 저장
    database.to_csv(database_path, index=False, encoding="utf-8")

    print(f"{company_name}|{file_name}|{page} conversion completed.\n")

    return det_res, output_data


def multi_extract_and_save_bounding_boxes(
    root_dir: str,
    extract_and_save_bounding_boxes: Callable[
        [str, str, str, str, int, int, int, float, str, float, bool], Tuple[Dict, List]
    ],
    **kwargs: Any,
) -> None:
    """
    루트 폴더 내에서 특정 형식의 이미지 파일을 처리하고,
    결과를 이미지 이름(확장자 제거)과 동일한 하위 폴더에 저장하는 함수.

    이 함수는 파일명이 "page_숫자" 형식인 이미지 파일을 식별한 후,
    주어진 extract_and_save_bounding_boxes를 사용해 각 이미지를 처리합니다.

    Args:
        root_dir (str): 이미지 파일이 저장된 루트 폴더 경로.
        extract_and_save_bounding_boxes (Callable[..., None]):
            단일 이미지를 처리하는 함수. 다음 매개변수를 가져야 합니다:
                - image_path (str): 처리할 이미지 파일의 경로.
                - res_path (str): 처리된 결과를 저장할 폴더 경로.
                - 추가적인 키워드 인자 (**kwargs).
        **kwargs (Any): extract_and_save_bounding_boxes에 전달될 추가 매개변수.

    Returns:
        None
    """
    # 이미지 확장자 정의
    valid_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".tiff")

    # 정규식 패턴: 파일명이 page_숫자 형식인지 확인
    page_pattern = re.compile(r"^page_\d+$")

    # 루트 폴더에서 파일 검색
    all_image_paths = [
        os.path.join(dp, f)
        for dp, dn, filenames in os.walk(root_dir)
        for f in filenames
        if f.lower().endswith(valid_extensions) and page_pattern.match(os.path.splitext(f)[0])
    ]

    for image_path in tqdm(all_image_paths, desc="Processing Images", unit="image"):
        # 현재 이미지 파일이 위치한 폴더 경로
        current_folder = os.path.dirname(image_path)

        # 파일 이름에서 확장자를 제거해 출력 폴더명 생성
        image_name = os.path.splitext(os.path.basename(image_path))[0]  # image_name(확장자 제거 파일 이름) 예시: page_1
        output_folder = os.path.join(current_folder, image_name)  # 이름이 파일 이름이랑 같은 폴더 경로

        # 출력 폴더가 이미 존재하면 삭제
        if os.path.exists(output_folder):
            print("The output folder already exists. It will be deleted and recreated.")
            shutil.rmtree(output_folder)

        # 출력 폴더 생성
        os.makedirs(output_folder, exist_ok=True)

        # extract_and_save_bounding_boxes 호출
        try:
            extract_and_save_bounding_boxes(image_path=image_path, res_path=output_folder, **kwargs)
            print("Save completed")
        except Exception as e:
            print(f"An error occurred while processing {image_path}: {e}")

    print("All images have been processed successfully.")


def pdf_parsing_pipeline(root_dir: str, db_path: str) -> None:
    """
    PDF 파일을 처리하는 파이프라인 함수로, 지정된 루트 디렉토리에서 PDF 파일을 이미지로 변환하고,
    변환된 이미지에서 바운딩 박스를 추출 및 저장하는 과정을 수행한 후 OCR을 거쳐서 텍스트화하여 데이터베이스를 만듭니다.

    Args:
        root_dir (str): PDF 파일과 이미지가 저장된 루트 디렉토리 경로.
        db_path (str): 데이터베이스 파일(csv)의 경로. PDF에서 추출된 바운딩 박스와 관련된 메타데이터(종목명, PDF 파일명, 페이지, 바운딩 박스 좌표 등)를 저장합니다.

    Returns:
        None: 이 함수는 결과를 저장하며, 값을 반환하지 않습니다.

    Workflow:
        1. `multi_pdf_to_image`: PDF 파일을 이미지로 변환하고 저장합니다.
        2. `multi_extract_and_save_bounding_boxes`: 변환된 이미지에서 바운딩 박스를 추출 및 저장합니다.
    """
    multi_pdf_to_image(root_dir=root_dir, db_path=db_path)

    shutil.copy(
        "/data/ephemeral/home/RF/data/database/database.csv", "/data/ephemeral/home/RF/data/database/database_temp.csv"
    )

    multi_extract_and_save_bounding_boxes(
        root_dir=root_dir,  # 이미지들이 저장된 루트 폴더
        extract_and_save_bounding_boxes=extract_and_save_bounding_boxes,
        database_path=db_path,
        model_path="/data/ephemeral/home/.cache/huggingface/hub/models--juliozhao--DocLayout-YOLO-DocStructBench/snapshots/8c3299a30b8ff29a1503c4431b035b93220f7b11/doclayout_yolo_docstructbench_imgsz1024.pt",  # 모델 경로
        imgsz=1024,
        line_width=5,
        font_size=20,
        split_images_foler_name="split_images",
        conf=0.2,
        threshold=0.05,
        verbose=False,
    )


pdf_parsing_pipeline(
    root_dir="/data/ephemeral/home/RF/data/original_data", db_path="/data/ephemeral/home/RF/data/database/database.csv"
)
