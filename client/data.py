import httpx

import config
from scraper.models.website_data import WebsiteData


async def upload_website_data(jobid: str, data: WebsiteData):
    async with httpx.AsyncClient() as client:
        r = await client.post(config.Config().API + '/data/upload/' + jobid, json=data.dict())
        print(r.json())
