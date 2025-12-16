import sys
from crawl import crawl_page

def main():
    args = sys.argv

    if len(args) < 2:
        print("no website provided")
        sys.exit(1)
    elif len(args) > 2:
        print("too many arguments provided")
        sys.exit(1)
    else:
        base_url = args[1]
        print(f"starting crawl of: {base_url}")
    
    page_data = crawl_page(base_url)

    print(f"found {len(page_data)} pages")
    for page in page_data.values():
        print(page["url"], "-", page["h1"])


if __name__ == "__main__":
    main()
