import sys
import asyncio
from crawl import crawl_site_async
from csv_report import write_csv_report


async def main():
    args = sys.argv

    if len(args) < 4:
        print("usage: python main.py <base_url> <max_concurrency> <max_pages>")
        sys.exit(1)
    elif len(args) > 4:
        print("too many arguments provided")
        sys.exit(1)
    
    base_url = args[1]
    if not args[2].isdigit():
        print("max_concurrency must be an integer")
        sys.exit(1)
    if not args[3].isdigit():
        print("max_pages must be an integer")
        sys.exit(1)

    max_concurrency = int(args[2])
    max_pages = int(args[3])
    
    print(f"starting crawl of: {base_url}")
    
    page_data = await crawl_site_async(base_url, max_concurrency, max_pages)

    for page in page_data.values():
        print(f"Found {len(page['outgoing_links'])} outgoing links on {page['url']}")
    
    write_csv_report(page_data)

    sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
