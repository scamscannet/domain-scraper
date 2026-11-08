import time

import httpx

from config import get_config
from client.exceptions import UnauthorizedException
from models.Job import Job
from log import logging


def get_or_wait_for_new_scraping_job() -> Job:
    error_counter = 0
    while error_counter < 100:
        try:
            with httpx.Client() as client:
                r = client.get(get_config().API + '/dispatcher/job', params={'node_id': get_config().NODE.node_id})

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
                raise UnauthorizedException("Unauthorized. Make sure the node id is valid, registered and active")
            else:
                logging.warning(f"Error while requestiong new job: {r.text}")
                error_counter += 1

            time.sleep(error_counter * error_counter + 2)
        except UnauthorizedException as e:
            logging.warning(f"Unauthorized")
            raise e
        except Exception as e:
            logging.warning(f"Requesting a job failed: {e}")
            time.sleep(10 if error_counter < 10 else error_counter * 2)
            error_counter += 1
