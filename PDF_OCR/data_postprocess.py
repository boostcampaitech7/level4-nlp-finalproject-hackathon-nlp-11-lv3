import pandas as pd
from bs4 import BeautifulSoup
import json
import os
import warnings
import requests
from dotenv import load_dotenv
import os
import time
load_dotenv()
warnings.filterwarnings("ignore")

"""    
    {//text 3
		"title":"24년 영업이익",
		"description":"{원문}", 
		"category":"text",
		"company":"naver",
		"securities":"hana",
		"page":"1",
		"date":"24.10.17",
		"path":"/cation/naver/kybo/1017/1/1_plain text_3.png"
	}
    api를 이용해 html을 query해 html에 대한 설명을 description에 넣어준다.
    이렇게 만들어진 데이터를 모두 모아서 하나의 파일로 저장한다.
    
"""    



class MakeData:
    def __init__(self):
        self.base_folder = 'ocr_results'
        self.output_folder = 'ocr_results'
        self.error_cnt = 0
        # 결과 저장할 폴더 생성
        self.existing_data = self.load_existing_data()
        self.failed_logs = self.load_failed_logs()

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
    def load_existing_data(self):
        try:
            with open('data.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    def load_failed_logs(self):
        try:
            with open('fail_logs.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def process_folders(self):
        data = self.existing_data
        try:
            # 첫 번째 처리 시도
            self._process_all_folders(data)
            
            # rate limit 오류가 있는 케이스 재처리
            retry_count = 0
            while retry_count < 3:  
                rate_limit_files = []
                for log in self.failed_logs:
                    if log.get('status_code') == '42901':  # rate limit 오류
                        rate_limit_files.append(log['file_path'])
                
                if not rate_limit_files:
                    break
                
                print(f"\n재시도 {retry_count + 1}: Rate limit 오류 파일 {len(rate_limit_files)}개 재처리 시작")
                time.sleep(60)  # rate limit 해제를 위해 1분 대기
                
                for file_path in rate_limit_files:
                    description = self.process_json_files(file_path)
                    if description:  # 성공적으로 처리된 경우
                        # 성공한 파일의 데이터 추가
                        path_parts = file_path.split(os.sep)
                        company = path_parts[1]
                        broker = path_parts[2]
                        page = path_parts[3]
                        broker_date = broker.split('_')[-1]
                        broker_name = broker_date.split('(')[0]
                        broker_date = broker_date.split('(')[1].replace(')', '')
                        
                        data.append({
                            "title": "",
                            "description": description,
                            "category": "table",
                            "company": company,
                            "securities": broker_name,
                            "page": page,
                            "date": broker_date,
                            "path": file_path
                        })
                
                retry_count += 1
            
            # 최종 데이터 저장
            with open('new_data/data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"전체 처리 중 오류 발생: {e}")
            self.save_failed_log("process_folders", str(e))

    def _process_all_folders(self, data):
        # 기존의 process_folders 로직을 여기로 이동
        for company in os.listdir(self.base_folder):
            company_path = os.path.join(self.base_folder, company)
            if not os.path.isdir(company_path):
                continue

            # 회사별 결과 폴더 생성
            company_output = os.path.join(self.output_folder, company)
            if not os.path.exists(company_output):
                os.makedirs(company_output)

            # 증권사별 폴더 순회
            for broker in os.listdir(company_path):
                broker_path = os.path.join(company_path, broker)
                if not os.path.isdir(broker_path):
                    continue

                # 증권사별 결과 폴더 생성
                broker_output = os.path.join(company_output, broker)
                if not os.path.exists(broker_output):
                    os.makedirs(broker_output)

                # 페이지별 폴더 순회
                for page in os.listdir(broker_path):
                    page_path = os.path.join(broker_path, page)
                    if not os.path.isdir(page_path):
                        continue

                    # 페이지별 결과 폴더 생성 헷갈려죽겠네
                    page_output = os.path.join(broker_output, page)
                    if not os.path.exists(page_output):
                        os.makedirs(page_output)

                    #html 파일 처리

                    for file in os.listdir(page_path):
                        if not file.lower().endswith(('.json')):
                            continue
                        description = self.process_json_files(os.path.join(page_path, file))
                        broker_date = broker.split('_')[-1]
                        broker_name = broker_date.split('(')[0]
                        broker_date = broker_date.split('(')[1].replace(')', '')
                        data_category = file.split('_')[1]
                        data.append({
                            "title": "",
                            "description": description,
                            "category": data_category,
                            "company": company,
                            "securities": broker_name,
                            "page": page,
                            "date": broker_date,
                            "path": f"./ocr_results/{company}/{broker}/{page}/{file}"
                        })

    def process_json_files(self, input_path):
           
        try:
            with open(input_path, 'r', encoding='utf-8-sig') as f:
                json_data = json.load(f)
            html = json_data["content"]["html"]

            # api를 이용해 html을 query해 html에 대한 설명을 description에 넣어준다.
            # 이렇게 만들어진 데이터를 모두 모아서 하나의 파일로 저장한다.

          
            api_url = 'https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003'
            studio_key = os.getenv('clova_studio_api_key')
            request_id = os.getenv('clova_request_id')
            headers = {
                        'Authorization': 'Bearer ' + studio_key,
                        'X-NCP-CLOVASTUDIO-REQUEST-ID':  request_id,
                        'Content-Type': 'application/json; charset=utf-8',
                    }
            #print(f"처리 완료: {output_base} : {file}")
            preset_text = [{"role":"system","content":"주어진 html은 table을 html로 표현한 것입니다. 해당 표에서 수치를 제외한 모든 항목의 정보를 문장으로 요약해서 알려주세요. 세부항목의 정보도 포함해주세요\n예시: 해당 표는 2022A부터 2026F까지의 매출액, 매출원가, 매출총이익, 판매비와관리비, 영업이익, ...(전부다) 재무정보를 제공하고 있습니다."},{"role":"user","content":html},{"role":"assistant","content":""}]
            request_data = {
                    'messages': preset_text,
                    'topP': 0.8,
                    'topK': 0,
                    'maxTokens': 400,
                    'temperature': 0.5,
                    'repeatPenalty': 5.0,
                    'stopBefore': [],
                    'includeAiFilters': True,
                    'seed': 0
                }
            # Query Per Minute 60회 이하로 고정
            time.sleep(1.1)
            response = requests.post(api_url, headers=headers, json=request_data)
            response_json = response.json()
            if response_json["status"]["code"] != "20000":
                error_message = response_json["status"]["message"]
                print(f"FAILED : {input_path} - {error_message}")
                self.save_failed_log(
                    input_path, 
                    error_message,
                    response_json["status"]["code"]
                )
                return ""
            else:
                respon_msg = response_json["status"]["code"]
                print(f"{input_path} SUCCESS : {respon_msg} ")
                return response_json["result"]["message"]["content"]
        
        except Exception as e:
            
            print(f"오류 발생: {e}")
            self.save_failed_log(input_path, str(e))
            return ""

    def save_failed_log(self, file_path, error_message, status_code=None):
        log_entry = {
            'file_path': file_path,
            'error_message': error_message,
            'status_code': status_code,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.failed_logs.append(log_entry)
        with open('fail_logs.json', 'w', encoding='utf-8') as f:
            json.dump(self.failed_logs, ensure_ascii=False, indent=2)


def main():
    
    processor = MakeData()
    processor.process_folders()
    
if __name__ == "__main__":
    main() 