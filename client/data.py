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


async def upload_website_data(jobid: str, data: ScrapingResult, assignment_id: str):
    post_data = data.website_data.dict()
    image_path = data.image_path
    if image_path:
        files = {'screenshot': open(image_path, 'rb')}
        async with httpx.AsyncClient() as client:
            r = await client.post(url=cfg.API + '/registry/node/upload/scrape', params={"assignment_id": assignment_id}, json=post_data, headers=headers)
            #i = await client.post(cfg.API + '/registry/node/upload/image', files=files, headers=headers)
    else:
        async with httpx.AsyncClient() as client:
            r = await client.post(cfg.API + '/registry/node/upload/scrape', params={"assignment_id": assignment_id}, json=post_data, headers=headers)

    if not r.status_code < 300:
        logging.error(f"Error while uploading scrape data: {r.text}")


async def report_website_status(job, type="issue", payload: dict = {}):
    report = ScraperReport(
        type=type,
        jobid=job.id,
        nodeid=cfg.NODE.node_id,
        payload=payload
    )
    await make_post_request_with_retires(url=cfg.API + '/data/scraper/upload/report', json=report.dict())

