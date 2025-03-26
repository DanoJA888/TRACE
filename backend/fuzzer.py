import requests
import time
import logging

class Fuzzer:
    def __init__(self):
        self.target_url = ''
        self.word_list = []
        self.http_method = 'GET'
        self.fuzz_results = [{'id': 'ID','response': 'Response','payload': 'Payload','length': 'Length'}]
        
    def execute_request(self, payload):
        url = self.target_url.replace("FUZZ", payload) if "FUZZ" in self.target_url else f"{self.target_url}/{payload}"#Send request with payload
        headers = {"User-Agent": "TRACE Fuzzer"}
        try:
            if self.http_method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif self.http_method == 'POST':
                response = requests.post(url, headers=headers, timeout=10)
            elif self.http_method == 'PUT':
                response = requests.put(url, headers=headers, timeout=10)
            else:
                return None
            
            return response
            
        except requests.RequestException as e:
            logging.error(f"Error with payload {payload}: {str(e)}")
            return None

    def process_fuzzer_response(self, response, payload):
        if not response:
            return None
            
        result = {
            'id': len(self.fuzz_results),
            'response': response.status_code,
            'payload': payload,
            'length': len(response.content)
        }
        self.fuzz_results.append(result)
        return result

    def fuzz(self):#run fuzzer
        if not self.target_url or not self.word_list:
            logging.error("Target URL and wordlist must be entered here. ")
            return False
            
        for payload in self.word_list:
            response = self.execute_request(payload)
            if response:
                self.process_fuzzer_response(response, payload)
        
        return True

    async def start_fuzz(self, fuzz_params):
        self.configure_fuzzer(fuzz_params)
        success = self.fuzz()
        return {
            'results': self.fuzz_results
        }

    def configure_fuzzer(self, fuzz_params):#fuzzer params
        self.target_url = fuzz_params.get('target_url', '')
  
        word_list = fuzz_params.get('word_list', [])#input worlists
        if isinstance(word_list, str) and word_list:
            self.word_list = [word.strip() for word in word_list.split(',') if word.strip()]#hangle commas in input
        else:
            self.word_list = word_list if isinstance(word_list, list) else []
            
        self.http_method = fuzz_params.get('http_method', 'GET')