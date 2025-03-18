import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from collections import deque

class Crawler:
    def __init__(self, start_url):
        self.start_url = start_url
        self.visited_urls = set()
        self.tree_structure = {}

    def fetch_page(self, url): #fetching html data
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200: # takes valid urls
                return response.text
        except requests.RequestException: #general exeption catching we will have an error handler class to handle this
            return None
        return None

    def extract_links(self, html, base_url):
        """Extracts and returns valid links from an HTML page."""
        soup = BeautifulSoup(html, "html.parser")
        links = set()
        for a_tag in soup.find_all("a", href=True):
            full_url = urljoin(base_url, a_tag["href"])
            if self.is_valid_url(full_url):
                links.add(full_url)
        return links

    def is_valid_url(self, url): #I think I wrote this wrong but this should effectively avoid a looping issue where the url visits itself or visits one from before
        parsed = urlparse(url)
        return parsed.netloc == urlparse(self.start_url).netloc and url not in self.visited_urls

    def crawl(self): #crawler process using a queue
        queue = deque([self.start_url])  # Use a queue to track URLs
        self.tree_structure[self.start_url] = []  # Initialize root in the tree

        while queue:
            url = queue.popleft()
            if url in self.visited_urls:
                continue

            print(f"Crawling: {url}")
            self.visited_urls.add(url)
            html = self.fetch_page(url)
            if html:
                links = self.extract_links(html, url)
                self.tree_structure[url] = list(links)  # Store links in the tree structure
                queue.extend(links)  # Add found links to the queue
                # time.sleep(1)  # sleep to avoid overloading servers can probably remove if needed

    def save_tree(self): #this will be merged or likely changed out of this code once we are provided code and team to work with on subsystem 1
        with open("crawl_tree.txt", "w") as file:
            for parent_url, children in self.tree_structure.items():
                file.write(f"{parent_url} -> {', '.join(children)}\n")

    def start(self): # starting crawling sequence
        self.crawl()
        self.save_tree()
        print("Crawl completed.")

# Start the crawler
if __name__ == "__main__":
    crawler = Crawler("http://books.toscrape.com/")  # Change this URL to test different websites will be something not needed once implemented through a sveltkit
    crawler.start()
