from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from crawler import Crawler
from fuzzer import Fuzzer
from typing import Optional, List, Union
import logging

# logs whenever an endpoint is hit using logger.info
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# params for fuzzer with only the first required inputs for testing
class FuzzRequest(BaseModel):
    target_url: str
    word_list: Union[List[str], str] = []
    http_method: str = 'GET'

'''
  for now basically just launches the crawl based on the form submitted by the user
'''
@app.post("/crawler")
async def launchCrawl(request: CrawlRequest):
  # converts request from CrawlRequest Object to dictionary
  crawler = Crawler()
  params_dict = request.model_dump()
  logger.info(request)
  crawl_results = await crawler.start_crawl(params_dict)
  logger.info(crawl_results)
  return crawl_results

@app.post("/fuzzer")
async def launchFuzz(request: FuzzRequest):
  # converting request from Object to dic
  fuzzer = Fuzzer()
  params_dict = request.model_dump()
  logger.info(request)
  fuzz_results = await fuzzer.start_fuzz(params_dict)
  logger.info(fuzz_results)
  return fuzz_results

# helps frontend and backend communicate (different ports for fastAPI and sveltekit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)