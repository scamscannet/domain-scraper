import time
from typing import Dict

import httpx

from config import get_config
from scraper.models.scraper.scraping_result import ScrapingResult
from log import logging


def _get_auth_headers() -> Dict[str, str]:
    return {
        "X-NODE-SECRET": get_config().TOKEN
    }

def make_post_request_with_retires(**args):
    tries = 1
    with httpx.Client() as client:
        while tries <= 5:
            try:
                r = client.post(**args)
                if 200 <= r.status_code < 300:
                    return True
            except Exception as e:
                logging.warning(f"Request to {args['url']} failed due to {e}")
            time.sleep(tries * tries)
            tries += 1
    return False


def upload_website_data(data: ScrapingResult, assignment_id: str):
    logging.info(f"Uploading scrape")
    scrape_upload_url = get_config().API + "/registry/node/upload/scrape"
    result = make_post_request_with_retires(
        url=scrape_upload_url,
        json=data.to_dict_without_screenshots(),
        params={"assignment_id": assignment_id},
        headers=_get_auth_headers()
    )
    if not result:
        logging.error(f"Error while uploading scrape data: {result}")
        return False

    logging.info(f"Scrape data uploaded successfully.")
    if data.screenshots:
        logging.info(f"Uploading screenshots.")
        scrape_upload_url = get_config().API + "/registry/node/upload/image"
        result = make_post_request_with_retires(
            url=scrape_upload_url,
            files=data.screenshots.dict(),
            headers=_get_auth_headers(),
            params={"assignment_id": assignment_id}
        )
        if not result:
            logging.error(f"Error while uploading screenshots. This shouldn't happen.")

    else:
        logging.info(f"No screenshots existing so no upload.")

