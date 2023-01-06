import logging
import time

import httpx

import config
from models.Job import Job
from log import logging

cfg = config.Config()


async def get_or_wait_for_new_scraping_job() -> Job:
    error_counter = 0
    while error_counter < 10:
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(cfg.API + '/dispatcher/get-job', params={'nodeid': cfg.NODE.nodeid})

            if r.status_code == 200:

                data = r.json()
                if not ("status_code" in data.keys() and data["status_code"] == 418): # TODO: check with fastapi returned statuscode
                    return Job(
                        domain=data['domain'],
                        id=data['jobid']
                    )
                # Check if it failed because no job was existing or if the query itself failed
                if "status_code" in data.keys() and data["status_code"] == 418:
                    error_counter = 0
                    pass
                else:
                    error_counter += 1

            time.sleep(2)
        except Exception as e:
            logging.warning(f"Requesting a job failed: {e}")
            time.sleep(10)
            error_counter += 1