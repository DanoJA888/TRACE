from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from crawler import Crawler
from typing import Optional
import logging
from fastapi.responses import StreamingResponse
import json

#logs whenever an endpoint is hit using logger.info
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#creates endpoints
app = FastAPI(title="Routes")

#params for crawler (optionals for optional params,
#both int | str in case they type into box and then delete input, prevents error and request goes through)
# note, with this set up, all inputs become strings, will handle in crawler process
class CrawlRequest(BaseModel):
    url: str
    depth: Optional[int | str] = ''
    max_pages: Optional[int | str] = ''
    user_agent: str = ''
    delay: Optional[str | int] = ''
    proxy: str = ''

'''
  for now basically just launches the crawl based on the form submitted by the user
'''
@app.post("/crawler")
async def launchCrawl(request: CrawlRequest):
    crawler = Crawler()
    params_dict = request.model_dump()
    logger.info(request)

    async def crawl_stream():
        async for update in crawler.start_crawl(params_dict):
            yield json.dumps(update) + "\n"

    return StreamingResponse(crawl_stream(), media_type="application/json")

#helps frontend and backend communicate (different ports for fastAPI and sveltekit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)