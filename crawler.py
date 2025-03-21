import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from collections import deque

class CrawledURLInfo:
    def __init__(self, url_in = '', title_in = '', word_count_in = '', char_count_in = '', links_found_in = '', words_in = []):
        self.url = url_in
        self.title = title_in
        self.word_count = word_count_in
        self.char_count = char_count_in
        self.link_count = links_found_in
        self.words = words_in


class Crawler:
    def __init__(self):
        self.start_url = ''
        self.crawl_depth = ''
        self.num_pages = ''
        self.proxy = ''
        self.user_agent_string = ''
        self. requests_per_sec = 0.0
        self.crawl_time = 0.0
        self.visited_urls = set()
        self.tree_structure = {}
        self.crawled_urls = {}

    def fetch_page(self, url): #fetching html data
        try:
            headers = {}
            if self.user_agent_string != '':
                headers["User-Agent"] = self.user_agent_string
            response = requests.get(url, timeout=5, headers=headers) # here use the user agent string for requests
            if response.status_code == 200: # takes valid urls
                return response.text
        except requests.RequestException: #general exeption catching we will have an error handler class to handle this
            return None
        return None

    def retreieve_links_to_crawl(self, parsed_html, base_url):
        """Extracts and returns valid links from an HTML page."""
        # soup = BeautifulSoup(html, "html.parser")
        links = set()
        for a_tag in parsed_html.find_all("a", href=True):
            full_url = urljoin(base_url, a_tag["href"])
            if self.is_valid_url(full_url):
                links.add(full_url)
        return links

    def is_valid_url(self, url): #I think I wrote this wrong but this should effectively avoid a looping issue where the url visits itself or visits one from before
        parsed = urlparse(url)
        return parsed.netloc == urlparse(self.start_url).netloc and url not in self.visited_urls
    
    #creates an object to store the info of each webpage
    def retreive_url_info(self, parsed_html, url, links):
        text = parsed_html.get_text()
        char_count = len(text)
        words= text.split()
        word_count = len(words)
        link_count = len(links)
        title = parsed_html.title.string

        url_info = CrawledURLInfo(url, title, word_count, char_count, link_count, words)
        return url_info
        pass

    def crawl(self): #crawler process using a queue
        start = time.time()
        queue = deque([self.start_url])  # Use a queue to track URLs
        self.tree_structure[self.start_url] = []  # Initialize root in the tree

        while queue:
            url = queue.popleft()

            #counts the depth of the current path and skips url if too deep
            if self.depth != '' and url != self.start_url:
                curr_url_path = urlparse(url).path
                url_depth = curr_url_path.count('/')
                if url_depth > self.depth:
                    continue

            if url in self.visited_urls:
                continue

            print(f"Crawling: {url}")
            self.visited_urls.add(url)
            html = self.fetch_page(url)
            if html:
                parsed_html = BeautifulSoup(html, "html.parser")
                # sets up crawled urls info
                links = self.retreieve_links_to_crawl(parsed_html, url)
                url_info = self.retreive_url_info(parsed_html, url, links)
                self.crawled_urls[len(self.crawled_urls)] = url_info
                url_id = len(self.crawled_urls) - 1
                print(str(url_id) , " | ", self.crawled_urls[url_id].url , " | " , self.crawled_urls[url_id].title, " | ", str(self.crawled_urls[url_id].word_count) , " | " , str(self.crawled_urls[url_id].char_count) 
                      , " | ", str(self.crawled_urls[url_id].link_count))
                self.tree_structure[url] = list(links)  # Store links in the tree structure
                queue.extend(links)  # Add found links to the queue
                # time.sleep(1)  # sleep to avoid overloading servers can probably remove if needed
            
            #if num pages crawled quota reached, strop crawling
            if self.num_pages != '' and len(self.tree_structure) == self.num_pages:
                break

        end = time.time()
        self.crawl_time = end - start
        self.requests_per_sec = round(((len(self.crawled_urls)) / self.crawl_time), 2)

    def save_tree(self): #this will be merged or likely changed out of this code once we are provided code and team to work with on subsystem 1
        with open("crawl_tree.txt", "w") as file:
            for parent_url, children in self.tree_structure.items():
                file.write(f"{parent_url} -> {', '.join(children)}\n")

    def start(self): # starting crawling sequence
        self.receive_url()
        self.receive_crawler_depth()
        self.receive_crawl_pages_desired()
        self.receive_proxy()
        self.receive_user_agent()
        self.crawl()
        self.save_tree()
        print("Crawl completed in " + str(round(self.crawl_time, 2)) + " seconds.")
        print("Requests/sec: " + str(self.requests_per_sec))

    #simple url validator (not necessary later probs)
    def validate_url_requested(self, url):
        if len(url) <=12:
            return False
        if (url[0:7] != "http://" and url [0:8] != "https://") or url[-5:] != ".com/":
            return False
        return True
    
    #function that receives the url from the user in terminal *will change once we integret ui*
    def receive_url(self):
        url = ''
        while True:
            url = input('Please input the target URL ')
            if self.validate_url_requested(url):
                #update base url for crawler class (dont think it should be an attribute of crawler class as we in theory only need one instance of crawler 
                #and should recieve test multiple times b ut can fix later with ui)
                self.start_url = url
                break
            print("Invalid URL! Please ensure you include 'https://' at the start and '.com' at the end")
    
    #function that recieves crawler depth desire
    def receive_crawler_depth(self):
        depth = -1
        while depth <= 0:
            try:
                depth = input("Please input how deep into a url you'd like to crawl. If no preference please enter an empty line '' ")
                if depth == '' or int(depth) >=1:
                    self.depth = depth if depth == '' else int(depth)
                    break
                print("Invalid depth!")
                depth = -1
            except:
                print("Not a number or empty line!")
                depth = -1
            

    #function that recieves total crawls desired
    def receive_crawl_pages_desired(self):
        num_pages = -1
        while num_pages <= 0:
            try:
                num_pages = input("Please input how many pages you want the crawl to retrieve. If no preference please enter an empty line '' ")
                if num_pages == '' or int(num_pages) >=1:
                    self.num_pages = num_pages if num_pages == '' else int(num_pages)
                    break
                print("Invalid number!")
                num_pages = -1
            except:
                print("Not a number or empty line!")
                num_pages = -1

    
    #function for receiving proxy desired 
    def receive_proxy(self):
        proxy = -1
        while proxy <= 0:
            try:
                proxy = input("Please input your desired proxy. If no preference please enter an empty line '' ")
                if proxy == '' or int(proxy) == 8080:
                    self.proxy = proxy if proxy == '' else int(proxy)
                    break
                print("Invalid proxy")
                proxy = -1
            except:
                print("Invalid proxy!")
                proxy = -1

    def receive_user_agent(self):
        user_agent = input("Please enter the user agent string of choice. If no preference please enter an empty line '' ")
        self.user_agent_string = user_agent
        
# Start the crawler
if __name__ == "__main__":
    # "http://books.toscrape.com/"
    crawler = Crawler()  # Change this URL to test different websites will be something not needed once implemented through a sveltkit
    crawler.start()
