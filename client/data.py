import httpx

import config
from scraper.models.scraping_result import ScrapingResult

cfg = config.Config()


async def upload_website_data(jobid: str, data: ScrapingResult):
        post_data = data.website_data.dict()
        image_path = data.image_path
        if image_path:
            files = {'screenshot': open(image_path, 'rb')}
            async with httpx.AsyncClient() as client:
                r = await client.post(cfg.API + '/data/upload/' + jobid, json=post_data)
            async with httpx.AsyncClient() as client:
                i = await client.post(cfg.API + '/data/upload-image/' + jobid, files=files)
        else:
            async with httpx.AsyncClient() as client:
                r = await client.post(cfg.API + '/data/upload/' + jobid, json=post_data)


async def mark_site_as_unreachable(job):
    async with httpx.AsyncClient() as client:
        r = await client.post(cfg.API + '/data/unreachable/' + job.id, params={'nodeid': cfg.NODE.nodeid})
