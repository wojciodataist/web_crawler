from urllib.parse import urlparse
from urllib.parse import urljoin
from bs4 import BeautifulSoup

def normalize_url(input_url):
    url = urlparse(input_url)
    new_url = url.netloc + url.path
    return new_url

def get_h1_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.h1.get_text()

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
