from bs4 import BeautifulSoup

from scraper.models.scraper.scraping_result import RawScrapingResult
from scraper.models.scraper.url import Url


class Module:
    name: str

    def check_if_eligible(self, url: Url) -> bool:
        return False

    def parse(self, url: Url, site_soup: BeautifulSoup, scrape: RawScrapingResult, **kwargs) -> dict:
        return {}
