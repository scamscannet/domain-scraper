import asyncio

import httpx

from scraper.engine.checks import check_for_http_or_https_and_return_url
from scraper.models.domain import Domain
from scraper.scraper import Scraper
from log import set_logger_to, logging

set_logger_to(logging.DEBUG)
scraper = Scraper()
async def run_scrape_with_timeout(domain):
    """Runs the scrape with a 30 seconds timeout. If it fails a TimeoutError is raised."""
    r = await asyncio.wait_for(scraper.scrape_website(domain), timeout=60 + 5)
    return r

x = asyncio.run(run_scrape_with_timeout(Domain(domain='artron', tld='net')))
print(x)