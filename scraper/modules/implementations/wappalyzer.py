import re

import httpx
from Wappalyzer import WebPage, Wappalyzer
from pydantic import BaseModel

from scraper.models.domain import Domain
from scraper.modules.base_module import Module
from scraper.modules.implementations.repository.wappalyzer import get_technologies, prepare_technology_file


class ModuleData(BaseModel):
    technologies: list = []


class ModuleImplementation(Module):
    name = "wappalyzer"

    def __init__(self):
        prepare_technology_file()
        get_technologies()

    def check_if_eligible(self, url: Domain):
        return True

    def parse(self, domain, site_soup, site_source, **kwargs) -> dict:
        return {}


