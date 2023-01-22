import asyncio
import os
import traceback

from scraper.scraper import Scraper
from scraper.models.exceptions.unreachable import UnreachableException
from scraper.models.exceptions.parsing_error import ParsingError
from client.jobs import get_or_wait_for_new_scraping_job
from client.data import upload_website_data, mark_site_as_unreachable, report_scraping_issue

from log import logging
from config import Config

logging.info("Starting Scraper")
scraper = Scraper()
cfg = Config()
async def run_scrape_with_timeout(domain):
    """Runs the scrape with a 30 seconds timeout. If it fails a TimeoutError is raised."""
    r = await asyncio.wait_for(scraper.scrape_website(domain), timeout=cfg.TIMEOUT + 5)
    return r



try:
    while True:
        logging.info("Waiting for a new job")
        job = asyncio.run(get_or_wait_for_new_scraping_job())
        logging.info(f"New Job found. Scraping {job.domain.domain}.{job.domain.tld}")
        try:
            data = asyncio.run(run_scrape_with_timeout(job.domain))
            logging.info(f"Scraping completed. Uploading data now")
            asyncio.run(upload_website_data(job.id, data))
            logging.info("Upload completed")
            if data.image_path:
                try:
                    os.remove(data.image_path)
                except:
                    pass
        except UnreachableException as e:
            logging.warning(f"Couldn't scrape {job.domain.domain}.{job.domain.tld} due to {e}. Marking as unreachable.")
            asyncio.run(mark_site_as_unreachable(job))

        except ParsingError or TimeoutError or Exception as e:
            logging.warning(f"Couldn't scrape {job.domain.domain}.{job.domain.tld} due to {e}. Marking as unscrapable.")
            asyncio.run(report_scraping_issue(job))
except Exception as e:
    logging.info(f"Terminating due to {e}.")

    scraper.terminate()
