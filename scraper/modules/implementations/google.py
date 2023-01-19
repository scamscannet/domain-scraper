import httpx
from pydantic import BaseModel

from scraper.models.domain import Domain
from scraper.modules.base_class import Module

class Response(BaseModel):
    total_results: int = 0
    organic: list = []
    sponsored: list = []

class ModuleImplementation(Module):
    _tlds: list = []
    name = "google_search"

    def __init__(self):
        domain_response = httpx.get("https://www.google.com/supported_domains")
        domains = domain_response.text.replace("\n", " ").split(" ")
        for domain in domains:
            try:
                tld = domain.split(".")[-1]
                self._tlds.append(tld)
            except Exception:
                pass

    def check_if_eligible(self, url: Domain):
        return url.domain == "google" and url.tld in self._tlds and "search" in url.path and "q" in url.query.keys()

    @property
    def tlds(self):
        return self._tlds


if __name__ == "__main__":
    c = ModuleImplementation()
