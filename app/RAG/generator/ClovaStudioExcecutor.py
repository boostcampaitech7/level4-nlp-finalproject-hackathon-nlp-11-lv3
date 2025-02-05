import backoff
import dotenv
import os
import http
import json
from http import HTTPStatus
dotenv.load_dotenv()


class RateLimitException(Exception):
    pass

class ClovaStudioExecutor:
    def __init__(self, host = "https://clovastudio.stream.ntruss.com/serviceapp/v1/chat-completions/HCX-003"):
        self.host = host
        self.api_key = os.getenv("NCP_CLOVASTUDIO_API_KEY")
        self.request_id = os.getenv("NCP_CLOVASTUDIO_REQUEST_ID")


    def _send_request(self, completion_request, endpoint):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-NCP-CLOVASTUDIO-REQUEST-ID": self.request_id,
            "Accept":"text/event-stream"
        }
        conn = http.client.HTTPSConnection(self.host)
        conn.request('POST', endpoint, json.dumps(completion_request), headers)
        response = conn.getresponse()
        status = response.status
        result = json.loads(response.read().decode(encoding='utf-8'))
        conn.close()
        return result, status
   
    @backoff.on_exception(backoff.expo, RateLimitException, max_tries=5, max_time=120, base=10)
    def execute(self, completion_request, endpoint):
        res, status = self._send_request(completion_request, endpoint)
        if status == HTTPStatus.OK:
            return res, status
        elif status == HTTPStatus.TOO_MANY_REQUESTS:
            raise RateLimitException
        else:
            raise Exception(f"API Error: {res}, {status}")
