from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import asyncio
import aiohttp


def normalize_url(input_url):
    url = urlparse(input_url)
    new_url = url.netloc + url.path
    new_url = new_url.rstrip("/")
    return new_url.lower()

def get_h1_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    h1 = soup.find("h1")
    if h1 is not None:
        return h1.get_text()
    else:
        return ""

def get_first_paragraph_from_html(html):
    paragraph_tag = None
    soup = BeautifulSoup(html, 'html.parser')
    if soup.main:
        paragraph_tag = soup.main.find('p')
    if paragraph_tag is None:
        paragraph_tag = soup.find('p')
    if paragraph_tag is not None:
        return paragraph_tag.get_text()
    else:
        return ""

def get_urls_from_html(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a')
    urls = []
    for link in links:
        href = link.get("href")
        if href:
            urls.append(urljoin(base_url, href))
    return urls

def get_images_from_html(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    image = soup.find_all('img')
    urls = []
    for img in image:
        src = img.get("src")
        if src:
            urls.append(urljoin(base_url, src))
    return urls

def extract_page_data(html, page_url):
    data = {}
    data["url"] = page_url
    data["h1"] = get_h1_from_html(html)
    data["first_paragraph"] = get_first_paragraph_from_html(html)
    data["outgoing_links"] = get_urls_from_html(html, page_url)
    data["image_urls"] = get_images_from_html(html, page_url)
    return data


class AsyncCrawler:
    def __init__(self, base_url, max_concurrency, max_pages):
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
        self.page_data = {}
        self.lock = asyncio.Lock()
        self.max_concurrency = max_concurrency
        self.max_pages = max_pages
        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.session = None
        self.should_stop = False
        self.all_tasks = set()

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
    
    async def add_page_visit(self, normalized_url):
        async with self.lock:
            if self.should_stop:
                return False
            if normalized_url in self.page_data:
                return False
            if len(self.page_data) >= self.max_pages:
                self.should_stop = True
                print("Reached maximum number of pages to crawl.")
                for task in self.all_tasks:
                    if not task.done():
                        task.cancel()
                return False
            return True
    
    async def get_html(self, url):
        try:
            async with self.session.get(
                url, headers={"User-Agent": "BootCrawler/1.0"}) as r:
                if r.status >= 400:
                    print(f"Error: HTTP {r.status} for {url}")
                    return None

                content_type = r.headers.get("Content-Type", "")
                if "text/html" not in content_type:
                    print(f"Error: Non-HTML content {content_type} for {url}")
                    return None
                
                return await r.text()
        
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    async def crawl_page(self, current_url):
        if self.should_stop:
            return

        current_url_obj = urlparse(current_url)
        if current_url_obj.netloc != self.base_domain:
            return

        normalized_url = normalize_url(current_url)

        is_new = await self.add_page_visit(normalized_url)
        if not is_new:
            return

        async with self.semaphore:
            print(f"Crawling {current_url} (Active: {self.max_concurrency - self.semaphore._value})")
            html = await self.get_html(current_url)
            if html is None:
                return

            page_info = extract_page_data(html, current_url)

            async with self.lock:
                self.page_data[normalized_url] = page_info

            next_urls = get_urls_from_html(html, self.base_url)
        
        if self.should_stop:
            return

        tasks = []
        for next_url in next_urls:
            task = asyncio.create_task(self.crawl_page(next_url))
            tasks.append(task)
            self.all_tasks.add(task)
        
        if tasks:
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
            finally:
                for task in tasks:
                    self.all_tasks.discard(task)

    async def crawl(self):
        await self.crawl_page(self.base_url)
        return self.page_data

async def crawl_site_async(base_url, max_concurrency, max_pages):
    async with AsyncCrawler(base_url, max_concurrency, max_pages) as crawler:
        return await crawler.crawl()
