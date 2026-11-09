import json
from collections import Counter
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

from scraper.models.scraper.scraping_result import RawScrapingResult
from scraper.models.scraper.url import Url
from scraper.modules.base_module import Module
from scraper.modules.helpers import registered_domain
from log import logging


class ModuleImplementation(Module):
    """Every host the browser sent a request to while loading the page (from the HAR): APIs, CDNs, trackers,
    payment providers, ... with the number of requests to each host.

    internal = same registered domain as the page (a.com, www.a.com, api.a.com), external = everything else."""
    name = "domains"

    def check_if_eligible(self, url: Url) -> bool:
        return True

    def parse(self, url: Url, site_soup: BeautifulSoup, scrape: RawScrapingResult, **kwargs) -> dict:
        try:
            entries = json.loads(scrape.har_bytes)["log"]["entries"]
        except Exception as e:
            logging.warning(f"Couldn't read HAR for domains: {e}")
            entries = []

        hosts = Counter()
        for entry in entries:
            request_url = urlsplit(entry.get("request", {}).get("url", ""))
            if request_url.scheme in ("http", "https", "ws", "wss") and request_url.hostname:
                hosts[request_url.hostname] += 1

        page_domain = registered_domain(scrape.final_url)
        internal, external = {}, {}
        for host, count in hosts.most_common():
            (internal if registered_domain(host) == page_domain else external)[host] = count

        return {
            "internal": internal,
            "external": external,
            "external_domains": sorted({registered_domain(host) for host in external}),
        }
