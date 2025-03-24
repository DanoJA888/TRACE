#fast api version 1.1
import requests
import time
from fastapi import FastAPI, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import uvicorn

# Create FastAPI app default values , title and description
app = FastAPI(title="Web Fuzzer API", description="API for web fuzzing operations")

# Define data models
class FuzzResult(BaseModel):#define structure of data being return by fuzzer
    parameter: str
    status_code: int
    content_length: int
    response_time: float

class FuzzRequest(BaseModel):#specify the data sent when start fuzzer
    target_url: str
    payloads: List[str]
    method: str = "GET"

class WebFuzzer:
    def __init__(self, target_url):
        self.target_url = target_url
        self.results = []
        self.is_fuzzing = False
    
    # Fetches response
    def fetch_response(self, url, param, method="GET"):
        # Send a request with a test parameter
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
    
    # Shows results
    def show_results(self):
        if not self.results:
            print("Nothing to Display")
            return
        print("\nFuzzer Results:")
        count = 1
        for result in self.results:
            print(f"Result {count}: {result['parameter']} - Status: {result['status_code']}, Length: {result['content_length']}")
            count += 1

# FastAPI routes
@app.get("/")
def read_root():
    return {"message": "Welcome to Web Fuzzer API"}

@app.post("/fuzz", response_model=List[FuzzResult])
def run_fuzzer(fuzz_request: FuzzRequest):
    #Run fuzzing with parameters
    if not fuzz_request.target_url:
        raise HTTPException(status_code=400, detail="Target URL is required")
    
    if not fuzz_request.payloads:
        raise HTTPException(status_code=400, detail="Payloads list is required")
    
    fuzzer = WebFuzzer(fuzz_request.target_url)
    results = fuzzer.fuzz(fuzz_request.payloads)
    formatted_results = []
    for result in results:
        formatted_result = FuzzResult(
            parameter=result["parameter"],
            status_code=result["status_code"],
            content_length=result["content_length"],
            response_time=result["response_time"])
        formatted_results.append(formatted_result)
    return formatted_results

@app.get("/test")
def test_endpoint():
    return {"status": "API is running status check"}

# run directly from this file (fuzzer.py) will require future change to run from main
if __name__ == "__main__":
    uvicorn.run("fuzzer:app", host="0.0.0.0", port=8000, reload=True)