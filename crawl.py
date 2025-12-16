from urllib.parse import urlparse
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests

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

def get_html(url):
    r = requests.get(url, headers={"User-Agent": "BootCrawler/1.0"})
    if r.status_code >= 400:
        r.raise_for_status()
    content_type = r.headers.get("Content-Type", "")
    if "text/html" not in content_type:
        raise ValueError("Response is not HTML")
    return r.text

def crawl_page(base_url, current_url=None, page_data=None):
    if current_url is None:
        current_url = base_url
    if page_data is None:
        page_data = {}

    normalized_url = normalize_url(current_url)

    if normalized_url in page_data:
        return page_data

    print(f"crawling {current_url}")

    try:
        html = get_html(current_url)
    except Exception as e:
        print(e)
        return page_data

    page_info = extract_page_data(html, current_url)
    page_data[normalized_url] = page_info

    urls = get_urls_from_html(html, current_url)
    for url in urls:
        crawl_page(base_url, url, page_data)

    return page_data
