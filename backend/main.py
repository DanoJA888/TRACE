from fastapi import FastAPI
from pydantic import BaseModel
from crawler import Crawler
from proxy_logic import handle_proxy_request, request_history, response_history

app = FastAPI()

class CrawlRequest(BaseModel):
    url: str
    depth: str = ""
    max_pages: str = ""
    user_agent: str = ""
    delay: str = ""
    proxy: str = ""

class ProxyRequest(BaseModel):
    url: str
    method: str = "GET"

@app.post("/crawl")
async def crawl_endpoint(config: CrawlRequest):
    try:
        crawler = Crawler()
        results = crawler.crawl(config.url, max_pages=int(config.max_pages or 5))
        return {
            "summary": {
                "total_crawled": len(results),
            },
            "results": results
        }
    except Exception as e:
        return {"error": str(e)}


@app.post("/proxy-request")
async def proxy_request(req: ProxyRequest):
    return handle_proxy_request(req.url, req.method)

@app.get("/proxy-history")
def get_history():
    return {
        "requestHistory": request_history,
        "responseHistory": response_history
    }
