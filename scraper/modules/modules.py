from scraper.models.domain import Domain, url_to_domain

ALL_MODULES = []

from scraper.modules.implementations import google

ALL_MODULES.append(google.ModuleImplementation())


def get_module_for_url(url: str | Domain):
    if isinstance(url, str):
        d = url_to_domain(url)
    else:
        d = url

    for module in ALL_MODULES:
        x = module.check_if_eligible(d)
        if x:
            return module
    return None