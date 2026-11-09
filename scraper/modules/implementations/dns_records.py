import uuid

import dns.exception
import dns.resolver
from bs4 import BeautifulSoup

from scraper.models.scraper.scraping_result import RawScrapingResult
from scraper.models.scraper.url import Url
from scraper.modules.base_module import Module
from scraper.modules.helpers import registered_domain

_RECORD_TYPES = ["A", "AAAA", "CNAME", "MX", "NS", "TXT", "SOA", "CAA"]

# Most common subdomain names. Real businesses tend to have several of these, throwaway domains rarely more than www.
_SUBDOMAIN_WORDLIST = [
    "www", "mail", "webmail", "smtp", "imap", "pop", "mx", "autodiscover", "autoconfig", "email",
    "api", "app", "admin", "portal", "dashboard", "login", "auth", "sso", "account", "my",
    "dev", "staging", "test", "beta", "demo",
    "shop", "store", "pay", "checkout", "blog", "news", "support", "help", "docs", "status",
    "cdn", "static", "assets", "img", "media", "m", "mobile",
    "vpn", "remote", "git", "ftp", "ns1", "ns2", "crm", "careers", "jobs",
]


class ModuleImplementation(Module):
    """DNS footprint of the registered domain. Established businesses usually have MX, SPF/DMARC, several TXT
    verifications (google-site-verification, MS=..., etc.) and many subdomains; throwaway domains usually don't.

    DNS itself can't list every record of a zone (zone transfers are refused almost everywhere), so:
    - records: every common record type of the domain is queried, plus the DMARC record at _dmarc.<domain>
    - subdomains: the names from _SUBDOMAIN_WORDLIST that resolve. No third-party service involved.
      If the domain has a wildcard record (a random name resolves too), every name would "exist", so the wordlist
      is skipped: wildcard is True and subdomains is None."""
    name = "dns"

    def check_if_eligible(self, url: Url) -> bool:
        return True

    def parse(self, url: Url, site_soup: BeautifulSoup, scrape: RawScrapingResult, **kwargs) -> dict:
        domain = registered_domain(scrape.final_url)
        resolver = dns.resolver.Resolver()
        resolver.lifetime = 5
        # Big answers (domains with many TXT records) don't fit the default 512-byte UDP packet and fall back to TCP,
        # which some resolvers don't answer. A bigger EDNS buffer keeps them on UDP.
        resolver.use_edns(0, 0, 4096)

        records = {}
        for record_type in _RECORD_TYPES:
            try:
                records[record_type] = [r.to_text() for r in resolver.resolve(domain, record_type)]
            except dns.exception.DNSException:
                records[record_type] = []
        try:
            records["DMARC"] = [r.to_text() for r in resolver.resolve(f"_dmarc.{domain}", "TXT")]
        except dns.exception.DNSException:
            records["DMARC"] = []

        try:
            resolver.resolve(f"{uuid.uuid4().hex}.{domain}", "A")
            wildcard = True
        except dns.exception.DNSException:
            wildcard = False

        subdomains = None
        if not wildcard:
            subdomains = []
            for name in _SUBDOMAIN_WORDLIST:
                try:
                    resolver.resolve(f"{name}.{domain}", "A")
                    subdomains.append(f"{name}.{domain}")
                except dns.exception.DNSException:
                    pass

        return {
            "domain": domain,
            "records": records,
            "record_counts": {record_type: len(values) for record_type, values in records.items()},
            "wildcard": wildcard,
            "subdomains": subdomains,
            "subdomain_count": len(subdomains) if subdomains is not None else None,
        }
