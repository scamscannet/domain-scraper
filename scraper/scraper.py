import asyncio
import datetime
import re
import time
import traceback

import tldextract
from pydantic import BaseModel
from selenium.common import TimeoutException
from selenium.common.exceptions import WebDriverException

from config import Config
from scraper.engine.browser import Browser
from scraper.engine.checks import check_for_http_or_https_and_return_url, get_ip_for_website
from scraper.models.code import Code
from scraper.models.exceptions.parsing_error import ParsingError
from scraper.models.exceptions.unreachable import UnreachableException
from scraper.models.javascript import JavaScript
from scraper.models.links import Links
from scraper.models.scraping_result import ScrapingResult, ScrapingWebsiteRedirect
from scraper.models.server import Server
from scraper.models.website_data import WebsiteData
from scraper.models.domain import Domain, url_to_domain
from scraper.modules.modules import get_module_for_url
from log import logging


class Scraper:
    _browser: Browser
    cfg: Config = Config()

    def __init__(self):
        self._browser = Browser()

    async def scrape_website(self, domain: Domain) -> ScrapingResult | ScrapingWebsiteRedirect:
        url = domain.to_url_without_protocol()
        module = get_module_for_url(domain)
        # Check for http or https
        try:
            redirect, verfied_url = await check_for_http_or_https_and_return_url(url)
            if redirect:
                return ScrapingWebsiteRedirect(
                    destination=verfied_url
                )

        except Exception:
            raise UnreachableException("Couldn't scrape website as it's unavailable")
        try:
            site_source, image_path = self._browser.get_website_sourcecode_and_screenshot(verfied_url, module)
        except (TimeoutException, WebDriverException):
            raise TimeoutError("Page loading timed out")
        except Exception as e:
            logging.warning(f"Scrape failed because of {e}")
            raise ParsingError("Couldn't scrape website")
        if not site_source:
            raise ParsingError("Couldn't scrape website")

        site_soup = self._browser.sourcecode_to_soup(site_source)
        page_title = site_soup.find('title').string if site_soup.find('title') else ''

        # Module
        module_data = module.parse(site_soup) if module else {}

        # Parse website Code
        javacript = JavaScript()
        for js_item in site_soup.select('script'):
            if js_item.has_attr("src"):
                link = js_item["src"]
                if link.startswith('//'):
                    javacript.external.append('https:' + link if verfied_url.startswith('https') else 'http:' + link)
                elif link.startswith('http') or link.startswith('https'):
                    javacript.external.append(link)
                elif link.startswith('/'):
                    javacript.internal.append(link)
            if js_item.contents:
                javacript.local.append(re.compile(r'\s+').sub(" ", js_item.string if js_item else ''))

        code = Code(
            title=page_title if page_title else "",
            html=site_source,
            text=re.compile(r'\s+').sub(" ", site_soup.get_text("\n")),
            # Remove all special characters to only have the text and single whitespaces
            javascript=javacript
        )

        # Parse Server
        server = Server(
            ip=get_ip_for_website(domain)
        )

        # Parse Links
        links_obj = Links(
            internal=[],
            external=[]
        )
        links = [solo["href"] for solo in site_soup.select("a") if solo.has_attr("href")]
        for link in links:
            if link.startswith('//'):
                links_obj.external.append('https:' + link if verfied_url.startswith('https') else 'http:' + link)
            elif link.startswith("/") or link.startswith("#"):
                links_obj.internal.append(link)
            else:
                links_obj.external.append(link)

        # Get new domain obj in case the browser url has been changed
        # domain = url_to_domain(verfied_url)

        # Process screenshot

        # Refresh Config every 4 hours to get a new ip
        if self.cfg.time + 60 * 4 < time.time():
            self.cfg = Config()

        website_data = WebsiteData(
            domain=domain,
            code=code,
            links=links_obj,
            server=server,
            node=self.cfg.NODE,
            modules={} if not module else {module.name: module_data},
            timestamp=datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
        )

        return ScrapingResult(
            website_data=website_data,
            image_path=image_path
        )

    def terminate(self):
        self._browser.close()
