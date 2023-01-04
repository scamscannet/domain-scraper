import datetime
import re
import time

import tldextract
from pydantic import BaseModel
from selenium.common import TimeoutException

from config import Config
from scraper.engine.browser import Browser
from scraper.engine.checks import check_for_http_or_https
from scraper.models.code import Code
from scraper.models.links import Links
from scraper.models.scraping_result import ScrapingResult
from scraper.models.server import Server
from scraper.models.website_data import WebsiteData
from log import logging
class Scraper:
    _browser: Browser
    cfg: Config = Config()

    def __init__(self):
        self._browser = Browser()

    async def scrape_website(self, url: str) -> ScrapingResult:

        # Check for http or https
        try:
            verfied_url = await check_for_http_or_https(url)
        except Exception:
            raise Exception("Couldn't scrape website as it's unavailable")
        try:
            site_source, image_path = self._browser.get_website_sourcecode_and_screenshot(verfied_url)
        except TimeoutException:
            raise TimeoutError("Page loading timed out")
        if not site_source:
            raise Exception("Couldn't scrape website")

        site_soup = self._browser.sourcecode_to_soup(site_source)
        page_title = site_soup.find('title').string

        # Parse website Code
        code = Code(
            title=page_title if page_title else "",
            html=site_source,
            text=re.compile(r'\s+').sub(" ", site_soup.get_text("\n")), # Remove all special characters to only have the text and single whitespaces
            javascript=[]
        )

        # Parse Server
        server = Server(
            ip="127.0.0.1"
        )

        # Parse Links
        internal_links = []
        external_links = []
        links = [solo["href"] for solo in site_soup.select("a") if solo.has_attr("href")]
        for link in links:
            if link.startswith("/"):  # or link.startswith("#"):
                internal_links.append(link)
            else:
                external_links.append(link)

        links = Links(
            internal=internal_links,
            external=external_links
        )

        tldext = tldextract.extract(verfied_url)
        domain = tldext.domain + '.' + tldext.suffix

        # Process screenshot

        # Refresh Config every 4 hours to get a new ip
        if self.cfg.time + 60 * 4 < time.time():
            self.cfg = Config()

        website_data = WebsiteData(
            domain=domain,
            url=verfied_url,
            code=code,
            links=links,
            server=server,
            node=self.cfg.NODE,
            modules={},
            timestamp=datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
        )

        return ScrapingResult(
            website_data=website_data,
            image_path=image_path
        )

    def terminate(self):
        self._browser.close()
