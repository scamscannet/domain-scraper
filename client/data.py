import asyncio
import time

import httpx

import config
from client.request_models.ScraperReport import ScraperReport
from scraper.models.scraper.scraping_result import ScrapingResult
from log import logging

cfg = config.Config()

headers = {
    "X-NODE-ID": cfg.NODE.node_id
}


async def make_post_request_with_retires(**args):
    tries = 1
    async with httpx.AsyncClient() as client:
        while tries <= 5:
            try:
                r = await client.post(**args)
                if 200 <= r.status_code < 300:
                    return True
            except Exception as e:
                logging.warning(f"Request to {args['url']} failed due to {e}")
            await asyncio.sleep(tries * tries)
            tries += 1
    return False


async def upload_website_data(data: ScrapingResult, assignment_id: str):
    completed = False
    counter = 0
    while not completed and counter < 10:
        post_data = data.website_data.dict()
        async with httpx.AsyncClient() as client:
            r = await client.post(url=cfg.API + '/registry/node/upload/scrape', params={"assignment_id": assignment_id},
                                  json=post_data, headers=headers)
        if not r.status_code < 300:
            logging.error(f"Error while uploading scrape data: {r.text}")
            counter += 1
            time.sleep(6 * counter)
            continue
        else:
            logging.info(f"Scrape data uploaded successfully.")
            completed = True
            counter = 0

            # Only upload images if scrape has been uploaded successfully
            if data.screenshots and completed:
                screenshot_completed = False
                while not screenshot_completed and counter < 10:
                    async with httpx.AsyncClient() as client:
                        await asyncio.sleep(2)
                        i = await client.post(cfg.API + '/registry/node/upload/image', params={"assignment_id": assignment_id},
                                              files=data.screenshots.dict(), headers=headers)

                        if not i.status_code < 300:
                            logging.error(f"Error while uploading screenshots: {i.text}")
                            counter += 1
                            time.sleep(6 * counter)
                        else:
                            screenshot_completed = True
                            logging.info(f"Screenshots uploaded successfully")

                if not screenshot_completed:
                    logging.warning(f"Screenshots couldn't be uploaded.")

    if not completed:
        logging.warning(f"Error while uploading screenshots. Retry limit exceeded.")
