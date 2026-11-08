from urllib.parse import urljoin, urlsplit

import tldextract
from bs4 import BeautifulSoup


def page_base_url(site_soup: BeautifulSoup, final_url: str) -> str:
    """URL that relative links on the page resolve against: <base href> if the page sets one, else the page URL."""
    base = site_soup.find("base", href=True)
    return urljoin(final_url, base["href"].strip()) if base else final_url


def resolve(base_url: str, link: str) -> str | None:
    """Absolute http(s) URL for a link as written in the HTML ('/a.js', 'a.js', '//cdn/a.js', 'https://...').
    Returns None for things that aren't fetchable resources (data:, javascript:, blob:, empty)."""
    link = (link or "").strip()
    if not link:
        return None
    absolute = urljoin(base_url, link)
    return absolute if urlsplit(absolute).scheme in ("http", "https") else None


def registered_domain(url: str) -> str:
    """'a.com' for 'https://cdn.a.com/x.js' – used to tell first-party from third-party resources."""
    return tldextract.extract(url).top_domain_under_public_suffix.lower()
