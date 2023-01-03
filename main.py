import asyncio
import traceback

from scraper.scraper import Scraper
from client.jobs import get_or_wait_for_new_scraping_job
from client.data import upload_website_data
from log import logging

logging.info("Starting Scraper")
scraper = Scraper()
try:
    while True:
        logging.info("Waiting for a new job")
        job = asyncio.run(get_or_wait_for_new_scraping_job())
        logging.info(f"New Job found. Scraping {job.domain}")
        try:
            data = asyncio.run(scraper.scrape_website(job.domain))
            logging.info(f"Scraping completed. Uploading data now")
            asyncio.run(upload_website_data(job.id, data))
            logging.info("Upload completed")
        except Exception as e:
            logging.warning(f"Couldn't scrape {job.domain} due to {e}")
except KeyboardInterrupt:
    scraper.terminate()