from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from crawler import Crawler
from fuzzer import Fuzzer
from typing import Optional, List, Union
import logging
from fastapi.responses import StreamingResponse
import json

# ---------- Logging ----------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- App ----------
app = FastAPI(title="TRACE API")

# ---------- CORS Middleware ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173"] if you want to be more secure
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Models ----------
class CrawlRequest(BaseModel):
    url: str
    depth: Optional[int | str] = ''
    max_pages: Optional[int | str] = ''
    user_agent: str = ''
    delay: Optional[str | int] = ''
    proxy: str = ''
    
class FuzzRequest(BaseModel):
    target_url: str
    word_list: Union[List[str], str] = []
    http_method: str = 'GET'

# ---------- Routes ----------
@app.post("/crawler")
async def launchCrawl(request: CrawlRequest):
    crawler = Crawler()
    params_dict = request.model_dump()
    logger.info(request)
    crawl_results = await crawler.start_crawl(params_dict)
    logger.info(crawl_results)
    return crawl_results
    crawler = Crawler()
    params_dict = request.model_dump()
    logger.info(request)

    async def crawl_stream():
        async for update in crawler.start_crawl(params_dict):
            yield json.dumps(update) + "\n"

    return StreamingResponse(crawl_stream(), media_type="application/json")

@app.post("/fuzzer")
async def launchFuzz(request: FuzzRequest):
    fuzzer = Fuzzer()
    params_dict = request.model_dump()
    logger.info(request)
    fuzz_results = await fuzzer.start_fuzz(params_dict)
    logger.info(fuzz_results)
    return fuzz_results