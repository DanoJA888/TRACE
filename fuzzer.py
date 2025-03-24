#first draft 1.1
import requests
import time  

class WebFuzzer:
    def __init__(self, target_url):
        self.target_url = target_url
        self.results = []
        self.is_fuzzing = False
    #Fetches response
    def fetch_response(self, url, param, method="GET"):
        #Send a request with a test parameter
        try:
            if method == "GET":
                response = requests.get(url, params={"fuzz": param}, timeout=10)
            elif method == "POST":
                response = requests.post(url, data={"fuzz": param}, timeout=10)
            else:
                raise ValueError(f"Error: {method}")
            
            return response
        except requests.RequestException as e:
            print(f"Error requesting '{param}': {e}")
            return None
    # test parameter
    def test_param(self, param):
        if param is None or param == "":
            return
        
        response = self.fetch_response(self.target_url, param)
        if not response:
            return
        
        # Storing the response data
        result = {
            "parameter": param,
            "status_code": response.status_code,
            "content_length": len(response.content),
            "response_time": response.elapsed.total_seconds()
        }
        
        self.results.append(result)
        return result
    
    def fuzz(self, payloads):
        self.is_fuzzing = True
        self.results = []
        
        start_time = time.time()
        print(f"Starting fuzzing of {self.target_url} with {len(payloads)} payloads")
        
        for param in payloads:
            result = self.test_param(param)
            if result:
                print(f"Tested: {param} | Status: {result['status_code']} | Length: {result['content_length']}")
        
        end_time = time.time()  
        duration = end_time - start_time
        print(f"Fuzzing completed: {duration:.2f} seconds")
        print(f"Tested {len(payloads)} parameters, got {len(self.results)} results")
        
        self.is_fuzzing = False
        return self.results
    #Shows results
    def show_results(self):
        if not self.results:
            print("Nothing to Display")
            return
        
        print("\nFuzzer Results:")
        count = 1
        for result in self.results:
            print(f"Result {count}: {result['parameter']} - Status: {result['status_code']}, Length: {result['content_length']}")
            count += 1

def run_test_fuzzer():
    # public API
    fuzzer = WebFuzzer("https://httpbin.org/get")
    
    # test payloads, or user specified payloads
    payloads = [
        "TestString",
        "111111",
    ]
    
    fuzzer.fuzz(payloads)
    fuzzer.show_results()  

if __name__ == "__main__":
    run_test_fuzzer()
    
#results screen and dashboard , front end folder backend folder, have at least 3 folders for 
#functionalities, 