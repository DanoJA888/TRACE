from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from crawler import Crawler
from typing import Optional
import logging
from fastapi.responses import StreamingResponse
import json
from fuzzer import Fuzzer
import os
import shutil

# logs whenever an endpoint is hit using logger.info
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("asyncio")

# creates endpoints
app = FastAPI(title="Routes")

# params for crawler (optionals for optional params,
# both int | str in case they type into box and then delete input, prevents error and request goes through)
# note, with this set up, all inputs become strings, will handle in crawler process
class CrawlRequest(BaseModel):
    url: str
    depth: Optional[int | str] = ''
    max_pages: Optional[int | str] = ''
    user_agent: str = ''
    delay: Optional[str | int] = ''
    proxy: str = ''

crawler = None
'''
 for now basically just launches the crawl based on the form submitted by the user
'''
@app.post("/crawler")
async def launchCrawl(request: CrawlRequest):
    global crawler
    crawler = Crawler()
    params_dict = request.model_dump()
    logger.info(request)
    
    async def crawl_stream():
        try:
            async for update in crawler.start_crawl(params_dict):
                yield json.dumps(update) + "\n"
        except Exception  as e:
            logger.error(f"Error in crawl stream: {e}", exc_info=True)
    
    return StreamingResponse(crawl_stream(), media_type="application/json")

# function that stops the execution of crawler when button is clicked
@app.post("/stop_crawler")
async def stopCrawler():
    global crawler
    if crawler:
        crawler.stop_crawl()
        crawler = Crawler()
        return {"message" : "Crawl stopping requested"}
    return {"message" : "nothing to stop"}

# Add fuzzer request model --- FUZZER
class FuzzRequest(BaseModel):
    target_url: str
    word_list: Optional[str] = ''
    cookies: Optional[str] = ''
    hide_status: Optional[str] = ''
    show_status: Optional[str] = ''
    http_method: str = 'GET'
    filter_by_content_length: Optional[str | int] = ''
    proxy: str = ''
    additional_parameters: Optional[str] = ''
    show_results: bool = True  # New parameter for toggling result visibility

# Add fuzzer endpoint 
@app.post("/fuzzer")
async def launchFuzz(request: FuzzRequest):
    fuzzer = Fuzzer()
    params_dict = request.model_dump()
    logger.info(request)
    
    async def fuzz_stream():
        async for update in fuzzer.run_scan(params_dict):
            yield json.dumps(update) + "\n"
    
    return StreamingResponse(fuzz_stream(), media_type="application/json")

# also need to Add wordlist upload endpoint
@app.post("/upload-wordlist")
async def upload_wordlist(file: UploadFile = File(...)):
    try:
        # Create directory if needed
        os.makedirs("./wordlist_uploads", exist_ok=True)
        
        # Save filename to local path
        filename = f"./wordlist_uploads/{file.filename}"
        
        with open(filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Wordlist file uploaded: {filename}")
        return {"path": filename}
    
    except Exception as e:
        logger.error(f"Error uploading wordlist file {str(e)}")
        return {"error !": str(e)}, 500

# helps frontend and backend communicate (different ports for fastAPI and sveltekit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)