from Wappalyzer import WebPage, Wappalyzer
from bs4 import BeautifulSoup
from pydantic import BaseModel

from scraper.models.domain import Domain
from scraper.modules.base_module import Module


class ModuleData(BaseModel):
    technologies: list = []


class ModuleImplementation(Module):
    name = "wappalyzer"

    def __init__(self):
        #prepare_technology_file()
        #get_technologies()
        self.wappalyzer = Wappalyzer.latest(update=True)

    def check_if_eligible(self, url: Domain):
        return True

    def parse(self, domain: Domain, site_soup: BeautifulSoup, site_source, **kwargs) -> dict:
        webpage = WebPage(
            url=domain.to_url_without_protocol(),
            html=site_source,
            headers=kwargs["headers"]
        )
        technologies = self.wappalyzer.analyze_with_versions_and_categories(webpage)
        return technologies

