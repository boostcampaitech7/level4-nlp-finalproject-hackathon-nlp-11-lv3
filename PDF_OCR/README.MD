# PDF_OCR 파이프라인

## 파이프라인 실행 방법

### 패키지 설치
``` bash
pip install -r requirements.txt
```

### 실행
``` bash
python pdf_parser.py -i "./pdf/input_pdf_folder"  -r
```

---

## 파일 구조

```
PDF_OCR/
├── config.py
├── folder_processor.py
├── pdf_parser.py
├── pdf_processor2.py
├── table_converter.py
├── requirements.txt
├── README.MD
├── pdf/
│   ├── input_pdf_folder/
│   │   ├── pdf_file1.pdf
│   │   ├── pdf_file2.pdf
│   │   └── ...
├── ocr_results/
│   ├── input_pdf_folder/
│   │   ├── pdf_file1/
│   │   │   ├── page_1/
│   │   │   │   ├── 1_plain text_3_result.json
│   │   │   │   └── ...
│   │   │   └── ...
│   │   └── ...
```
---

## 파이프라인 설명

1. PDF 파일을 이미지로 변환 (PDF -> 이미지)
2. 이미지를 바운딩 박스로 추출 (DocLayout-YOLO) (이미지 -> 바운딩 박스)
3. OCR 처리 (Clova OCR API) (바운딩 박스 -> OCR 결과(json))
4. OCR 결과를 테이블로 변환 (OCR 결과 -> 테이블(csv))

