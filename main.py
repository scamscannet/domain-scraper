import asyncio
import traceback

from scraper.scraper import Scraper
from client.jobs import get_or_wait_for_new_scraping_job
from client.data import upload_website_data

if __name__ == '__main__':
    scraper = Scraper()
    try:
        while True:
            job = asyncio.run(get_or_wait_for_new_scraping_job())
            data = asyncio.run(scraper.scrape_website(job.domain))
            asyncio.run(upload_website_data(job.id, data))
    except Exception as e:
        print(traceback.format_exc())
        print(e)
        scraper.terminate()
