import asyncio
import logging
import time

import httpx

import config
from client.request_models.ScraperReport import ScraperReport
from scraper.models.scraping_result import ScrapingResult
from log import logging

cfg = config.Config()


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


async def upload_website_data(jobid: str, data: ScrapingResult):
    post_data = data.website_data.dict()
    image_path = data.image_path
    full_size_image_path = data.full_size_image_path
    async with httpx.AsyncClient() as client:
        r = await client.post(url=cfg.API + '/data/scraper/upload/scrape/' + jobid, json=post_data)

    if image_path:
        files = {'screenshot': open(image_path, 'rb')}
        async with httpx.AsyncClient() as client:
            i = await client.post(cfg.API + '/data/scraper/upload/image/' + jobid + "/" + cfg.NODE.nodeid, files=files)
    if full_size_image_path:
        files = {'screenshot': open(full_size_image_path, 'rb')}
        async with httpx.AsyncClient() as client:
            i = await client.post(cfg.API + '/data/scraper/upload/full-image/' + jobid + "/" + cfg.NODE.nodeid, files=files)



async def report_website_status(job, type="issue", payload: dict = {}):
    report = ScraperReport(
        type=type,
        jobid=job.id,
        nodeid=cfg.NODE.nodeid,
        payload=payload
    )
    await make_post_request_with_retires(url=cfg.API + '/data/scraper/upload/report', json=report.dict())

