import asyncio
import time

from scraper.models.scraper.domain import url_to_domain
from scraper.models.scraper.scraping_result import ScrapingWebsiteRedirect, ScrapingResult
from scraper.models.scraper.website_data import WebsiteData
from scraper.scraper import Scraper
from scraper.models.exceptions.unreachable import UnreachableException
from scraper.models.exceptions.parsing_error import ParsingError
from client.jobs import get_or_wait_for_new_scraping_job
from client.data import upload_website_data

from log import logging
from config import Config

logging.info("Starting Scraper")
scraper = Scraper()
cfg = Config()
async def run_scrape_with_timeout(domain):
    """Runs the scrape with a 30 seconds timeout. If it fails a TimeoutError is raised."""
    r = await asyncio.wait_for(scraper.scrape_website(domain), timeout=cfg.TIMEOUT * 2)
    return r



try:
    while True:
        try:
            logging.info("Waiting for a new job")
            job = asyncio.run(get_or_wait_for_new_scraping_job())
            try:
                # Check if URL is valid
                logging.info(f"New Job found. Scraping {job.domain.to_url_without_protocol()}")

                data = asyncio.run(run_scrape_with_timeout(job.domain))
                if isinstance(data, ScrapingWebsiteRedirect):
                    redirect_domain = url_to_domain(data.destination)

                    logging.info(f"Detected redirect to {redirect_domain.to_url_without_protocol()}. Uploading redirect.")

                    website_data = WebsiteData(
                        status="redirect",
                        domain=job.domain,
                        redirect=redirect_domain
                    )

                    scraping_result = ScrapingResult(
                        website_data=website_data
                    )
                    asyncio.run(upload_website_data(scraping_result, job.id))
                    logging.info("Upload completed")


                else:
                    logging.info(f"Scraping completed. Uploading data.")
                    asyncio.run(upload_website_data(data, job.id))
                    logging.info("Upload completed")

            except UnreachableException as e:
                logging.warning(f"Couldn't scrape {job.domain.domain}.{job.domain.tld} due to {e}. Marking as unreachable.")
                website_data = WebsiteData(
                    status="offline",
                    domain=job.domain
                )
                scraping_result = ScrapingResult(
                    website_data=website_data
                )
                asyncio.run(upload_website_data(scraping_result, job.id))

            except (ParsingError, TimeoutError, Exception) as e:
                logging.warning(f"Couldn't scrape {job.domain.domain}.{job.domain.tld} due to {e}. Marking as usncrapable.")

                website_data = WebsiteData(
                    status="error",
                    domain=job.domain
                )
                scraping_result = ScrapingResult(
                    website_data=website_data
                )
                asyncio.run(upload_website_data(scraping_result, job.id))
        except Exception as e:
            logging.warning(f"An error occured: {e} = {type(e)}. Retsarting scraper with timeout")
            time.sleep(180)
            logging.info(f"Restarting scraper")

except Exception as e:
    logging.info(f"Terminating due to {e}.")

    scraper.terminate()
