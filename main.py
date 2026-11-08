import time

from scraper.models.scraper.scraping_result import ScrapingResult
from scraper.models.scraper.website_data import WebsiteData
from scraper.scraper import Scraper
from scraper.exceptions import ScraperError
from client.jobs import get_or_wait_for_new_scraping_job
from client.data import upload_website_data

from log import logging
from config import Config, get_config

logging.info("Checking environment")
r = Config.check_env()
if r:
    logging.info(f"Environment check passed. Starting scraper.")
else:
    logging.info(f"Environment check failed. Aborting.")
    exit()

logging.info("Starting Scraper")
try:
    scraper = Scraper()
except:
    logging.info(f"Scraper failed. Aborting.")
    exit()


def upload_error(job):
    """Reports the job back as status "error" so the backend doesn't keep it assigned forever."""
    scraping_result = ScrapingResult(
        website_data=WebsiteData(
            status="error",
            url=job.domain,
            node=get_config().NODE
        )
    )
    upload_website_data(scraping_result, job.id)


try:
    while True:
        try:
            logging.info("Waiting for a new job")
            job = get_or_wait_for_new_scraping_job()
            try:
                # Check if URL is valid
                logging.info(f"New Job found. Scraping {job.domain.to_url_without_protocol()}")
                scraping_result = scraper.scrape_website(job.domain)

                logging.info(f"Scraping completed. Website has status: {scraping_result.website_data.status} Uploading data!")
                upload_website_data(scraping_result, job.id)

                logging.info("Upload completed.")

            except ScraperError as e:
                logging.warning(f"ERROR: Couldn't scrape {job.domain.domain}.{job.domain.tld} due to {e}. Marking as unscrapable.")
                upload_error(job)
            except Exception as e:
                logging.critical(f"Error while parsing: {e}. This likely is a internal error. Marking as unscrapable.")
                upload_error(job)

            if get_config().DEVELOPMENT:
                break
        except Exception as e:
            logging.warning(f"An error occured: {e} = {type(e)}. Restarting scraper with timeout")
            time.sleep(180)
            logging.info(f"Restarting scraper")

except Exception as e:
    logging.info(f"Terminating due to {e}.")

finally:
    scraper.terminate()
