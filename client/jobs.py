import time

import httpx

import config
from models.Job import Job

cfg = config.Config()

async def get_or_wait_for_new_scraping_job() -> Job:
    while True:
        async with httpx.AsyncClient() as client:
            r = await client.get(cfg.API + '/dispatcher/get-job', params={'nodeid': cfg.NODE.nodeid})

        if r.status_code == 200:
            data = r.json()
            if not ("status_code" in data.keys() and data["status_code"] == 418): # TODO: check with fastapi returned statuscode
                domain = data['domain'] + '.' + data['tld']
                jobid = data['jobid']
                return Job(
                    domain=domain,
                    id=jobid
                )

        time.sleep(2)

