import asyncio
import logging
import time

import httpx

import config
from client.request_models.ScraperReport import ScraperReport
from scraper.models.scraping_result import ScrapingResult
from log import logging

cfg = config.Config()

headers = {
    "X-NODE-ID": "123"
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
    post_data = data.website_data.dict()
    async with httpx.AsyncClient() as client:
        r = await client.post(url=cfg.API + '/registry/node/upload/scrape', params={"assignment_id": assignment_id},
                              json=post_data, headers=headers)
    if not r.status_code < 300:
        logging.error(f"Error while uploading scrape data: {r.text}")
    else:
        logging.info(f"Scrape data uploaded successfully.")

        # Only upload images if scrape has been uploaded successfully
        if data.screenshots:
            async with httpx.AsyncClient() as client:
                    files = {
                        "full": ("full.png", data.screenshots.full),
                        "visible": ("visible.png", data.screenshots.visible)
                    }
                    await asyncio.sleep(2)
                    i = await client.post(cfg.API + '/registry/node/upload/image', params={"assignment_id": assignment_id}, files=data.screenshots.dict(), headers=headers)

                    if not i.status_code < 300:
                        logging.error(f"Error while uploading screenshots: {i.text}")




async def report_website_status(job, type="issue", payload: dict = {}):
    report = ScraperReport(
        type=type,
        jobid=job.id,
        nodeid=cfg.NODE.node_id,
        payload=payload
    )
    await make_post_request_with_retires(url=cfg.API + '/data/scraper/upload/report', json=report.dict())

