import socket
from urllib.parse import urlsplit

import httpx
from bs4 import BeautifulSoup
from ipwhois import IPWhois

from scraper.models.scraper.scraping_result import RawScrapingResult
from scraper.models.scraper.url import Url
from scraper.modules.base_module import Module
from scraper.modules.helpers import registered_domain
from log import logging

_WHOIS_API = "https://whois.backend.scamscan.net"
_TIMEOUT = 20  # seconds


class ModuleImplementation(Module):
    """WHOIS of the registered domain (from our who_dat instance, stored as returned) and of the IP the page's host
    resolves to (RDAP via ipwhois: network, owner, ASN, country). A failed lookup is stored as None."""
    name = "whois"

    def check_if_eligible(self, url: Url) -> bool:
        return True

    def parse(self, url: Url, site_soup: BeautifulSoup, scrape: RawScrapingResult, **kwargs) -> dict:
        domain = registered_domain(scrape.final_url)
        result = {"domain": None, "ip": None, "ip_whois": None}

        try:
            r = httpx.get(f"{_WHOIS_API}/{domain}", timeout=_TIMEOUT)
            r.raise_for_status()
            result["domain"] = r.json()
        except Exception as e:
            logging.warning(f"Domain whois for {domain} failed: {e}")

        try:
            result["ip"] = socket.gethostbyname(urlsplit(scrape.final_url).hostname)
            result["ip_whois"] = IPWhois(result["ip"], timeout=_TIMEOUT).lookup_rdap(depth=1)
        except Exception as e:
            logging.warning(f"IP whois for {scrape.final_url} failed: {e}")

        return result
