from bs4 import BeautifulSoup

from scraper.models.scraper.domain import Domain


class Module:
    name: str

    def check_if_eligible(self, url: Domain) -> bool:
        return False

    def parse(self, domain: Domain, site_soup: BeautifulSoup, site_source, **kwargs) -> dict:
        return {}
