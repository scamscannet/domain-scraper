from scraper.models.scraper.url import Url, parse_url

ALL_MODULES = []

from scraper.modules.implementations import google, javascript, metadata, text, whois, dns_records, domains

ALL_MODULES.append(google.ModuleImplementation())
ALL_MODULES.append(javascript.ModuleImplementation())
ALL_MODULES.append(text.ModuleImplementation())
ALL_MODULES.append(metadata.ModuleImplementation())
ALL_MODULES.append(whois.ModuleImplementation())
ALL_MODULES.append(dns_records.ModuleImplementation())
ALL_MODULES.append(domains.ModuleImplementation())


def get_module_for_url(url: str | Url):
    if isinstance(url, str):
        d = parse_url(url)
    else:
        d = url

    for module in ALL_MODULES:
        x = module.check_if_eligible(d)
        if x:
            yield module
    return None