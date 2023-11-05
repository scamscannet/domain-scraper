from scraper.models.scraper.domain import Domain, url_to_domain

ALL_MODULES = []

from scraper.modules.implementations import google
from scraper.modules.implementations import wappalyzer

ALL_MODULES.append(google.ModuleImplementation())
ALL_MODULES.append(wappalyzer.ModuleImplementation())


def get_module_for_url(url: str | Domain):
    if isinstance(url, str):
        d = url_to_domain(url)
    else:
        d = url

    for module in ALL_MODULES:
        x = module.check_if_eligible(d)
        if x:
            yield module
    return None