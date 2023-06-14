import logging
import time

import httpx

import config
from client.exceptions import UnauthorizedException
from models.Job import Job
from log import logging

cfg = config.Config()


async def get_or_wait_for_new_scraping_job() -> Job:
    error_counter = 0
    while error_counter < 10:
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(cfg.API + '/registry/node/job', params={'node_id': cfg.NODE.node_id})

            if r.status_code == 200:
                data = r.json()
                return Job(
                    domain=data['domain'],
                    id=data['assignment_id']
                )
                # Check if it failed because no job was existing or if the query itself failed
            elif r.status_code == 418:
                error_counter = 0
            elif r.status_code == 401:
                raise UnauthorizedException("Unauthorized. Make sure the nodeid is valid, registered and active")
            else:
                error_counter += 1

            time.sleep(error_counter * error_counter + 2)
        except UnauthorizedException as e:
            raise e
        except Exception as e:
            logging.warning(f"Requesting a job failed: {e}")
            time.sleep(10)
            error_counter += 1
