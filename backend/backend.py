from fastapi import FastAPI, Query
from crawler import Crawler

app = FastAPI(title="Routes")
crawler = Crawler()

'''
  for now basically just launches the crawl based on the form submitted by the user
'''
@app.post("/crawl")
async def launchCrawl(url = Query(...), depth = Query(3), crawler_pages = Query(25), user_agent = Query(""), delay = Query(0), proxy = Query(0)):
  current_crawl_results = await crawler.start_crawl()
  #need to wait for front end form submission done by @JAMES ROBINSON (will be ready tomorrow @ 12)
  
  pass