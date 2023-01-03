import httpx

import config
from scraper.models.website_data import WebsiteData

cfg = config.Config()


async def upload_website_data(jobid: str, data: WebsiteData):
    async with httpx.AsyncClient() as client:
        r = await client.post(cfg.API + '/data/upload/' + jobid, json=data.dict())
        print(r.json())
