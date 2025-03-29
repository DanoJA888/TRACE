import requests
import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

app = FastAPI()

#something chat recommended need to figure this out
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/fuzzer/stream")
async def start_fuzzing(request: Request):
    fuzz_params = await request.json()
    fuzzer = Fuzzer()

    def log_stream():
        for line in fuzzer.run_and_stream_logs(fuzz_params):
            yield f"data: {line}\n\n"

    return StreamingResponse(log_stream(), media_type="text/event-stream")    

class Fuzzer:
    def __init__(self):
        self.target_url = ''
        self.word_list = []
        self.http_method = 'GET'
        self.fuzz_results = []
        self.cookies = ''
        self.hide_codes = ''
        self.show_only = ''
        self.content_length = ''
        self.extra_params = ''
        self.start_time = 0
        self.end_time = 0
        self.filtered_requests = 0
        self.processed_requests = 0

    def execute_request(self, payload):
        url = self.target_url.replace("FUZZ", payload) if "FUZZ" in self.target_url else f"{self.target_url}/{payload}"
        
        headers = {
            "User-Agent": "TRACE Fuzzer"
        }
        
        #cookies
        if self.cookies:
            headers["Cookie"] = self.cookies

        try:
            start_time = time.time() 

            if self.http_method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif self.http_method == 'POST':
                response = requests.post(url, headers=headers, timeout=10)
            elif self.http_method == 'PUT':
                response = requests.put(url, headers=headers, timeout=10)
            else:
                return None, 0.0  # Fallback

            elapsed_time = round(time.time() - start_time, 3)  

            logging.info(f"[DEBUG] Received response for {payload}: {response.status_code} in {elapsed_time}s")
            return response, elapsed_time  
        except requests.RequestException as e:
            logging.warning(f"RequestException for {payload}: {str(e)}")
            return None, 0.0

    def process_fuzzer_response(self, response, payload, elapsed_time):
        content = response.text
        lines = content.count('\n') + 1
        words = len(content.split())
        chars = len(content)
        error = response.status_code >= 400 or chars == 0

        result = {
            'id': len(self.fuzz_results),
            'response': response.status_code,
            'lines': lines,
            'words': words,
            'chars': chars,
            'payload': payload,
            'length': elapsed_time,
            'error': error
        }

        self.fuzz_results.append(result)
        return result
    
    def should_include_response(self, response_code, response_length):
        # Parse hide_codes
        if self.hide_codes:
            hidden = [int(code.strip()) for code in self.hide_codes.split(',') if code.strip().isdigit()]
            if response_code in hidden:
                return False

        # Parse show_only
        if self.show_only:
            logging.info(f"show_only raw: {self.show_only} ({type(self.show_only)})")
            allowed = [int(code.strip()) for code in self.show_only.split(',') if code.strip().isdigit()]
            if response_code not in allowed:
                return False

        # Parse content_length filters
        if self.content_length:
            length_filters = self.content_length.split(',')
            for f in length_filters:
                f = f.strip()
                if f.startswith('>') and response_length <= int(f[1:]):
                    return False
                elif f.startswith('<') and response_length >= int(f[1:]):
                    return False
                elif f.isdigit() and response_length != int(f):
                    return False
                
        return True

    def fuzz(self):
        if not self.target_url or not self.word_list:
            logging.error("Target URL and wordlist must be entered.")
            return False

        logging.info(f"Wordlist being used: {self.word_list}")
        
        self.start_time = time.time() 
        self.processed_requests = 0
        self.filtered_requests = 0

        for payload in self.word_list:
            response, elapsed_time = self.execute_request(payload)
            self.processed_requests += 1

            if response is not None:
                if self.should_include_response(response.status_code, len(response.content)):
                    self.process_fuzzer_response(response, payload, elapsed_time)
                else:
                    self.filtered_requests += 1

        self.end_time = time.time()
        return True

    async def start_fuzz(self, fuzz_params):
        self.configure_fuzzer(fuzz_params)
        success = self.fuzz()

        running_time = round(self.end_time - self.start_time, 3)
        processed = self.processed_requests
        filtered = self.filtered_requests
        req_per_sec = round(processed / running_time, 3) if running_time > 0 else 0.0

        return {
            "fuzzer results": self.fuzz_results,
            "stats": {
                "running_time": running_time,
                "processed_requests": processed,
                "filtered_requests": filtered,
                "requests_per_sec": req_per_sec
            }
        }

    def configure_fuzzer(self, fuzz_params):
        self.target_url = fuzz_params.get('target_url', '')

        word_list = fuzz_params.get('word_list', [])
        if isinstance(word_list, str) and word_list:
            self.word_list = [word.strip() for word in word_list.split(',') if word.strip()]
        else:
            self.word_list = word_list if isinstance(word_list, list) else []

        self.http_method = fuzz_params.get('http_method', 'GET')
        self.cookies = fuzz_params.get('cookies', '')
        self.hide_codes = fuzz_params.get('hide_codes', '')
        self.show_only = fuzz_params.get('show_only', '')
        self.content_length = fuzz_params.get('content_length', '')
        self.extra_params = fuzz_params.get('extra_params', '')

    def run_and_stream_logs(self, fuzz_params):
        self.configure_fuzzer(fuzz_params)

        self.start_time = time.time()
        self.processed_requests = 0
        self.filtered_requests = 0
        self.fuzz_results = []

        yield f"Running fuzzer with {len(self.word_list)} payloads..."

        for payload in self.word_list:
            response, elapsed = self.execute_request(payload)
            self.processed_requests += 1

            log = f"[{self.processed_requests}] {payload} => "
            if response:
                log += f"{response.status_code} ({elapsed}s)"
                if self.should_include_response(response.status_code, len(response.content)):
                    self.process_fuzzer_response(response, payload, elapsed)
                else:
                    self.filtered_requests += 1
            else:
                log += "Error"
                self.filtered_requests += 1

            yield log
            time.sleep(0.2)  # slow down stream to visualize updates

        self.end_time = time.time()

        yield f"Done. Total: {self.processed_requests}, Filtered: {self.filtered_requests}"
            