import httpx

import config
from scraper.models.scraping_result import ScrapingResult

cfg = config.Config()


async def upload_website_data(jobid: str, data: ScrapingResult):
    async with httpx.AsyncClient() as client:
        post_data = data.website_data.dict()
        image_path = data.image_path
        if image_path:
            files = {'screenshot': open(image_path, 'rb')}
            r = await client.post(cfg.API + '/data/upload/' + jobid, json=post_data)
            i = await client.post(cfg.API + '/data/upload-image/' + jobid, files=files)
        else:
            r = await client.post(cfg.API + '/data/upload/' + jobid, json=post_data)


async def mark_site_as_unreachable(job):
    async with httpx.AsyncClient() as client:
        r = await client.post(cfg.API + '/data/unreachable/' + job.id, params={'nodeid': cfg.NODE.nodeid})
