import json
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

from scraper.models.scraper.scraping_result import RawScrapingResult
from scraper.models.scraper.url import Url
from scraper.modules.base_module import Module
from scraper.modules.helpers import page_base_url, registered_domain, resolve
from log import logging

_JS_MIME_MARKERS = ("javascript", "ecmascript")
_JS_EXTENSIONS = (".js", ".mjs", ".cjs")


class ModuleImplementation(Module):
    """Collects the URLs of all JavaScript files the page loads – no file contents.

    Two sources, merged and de-duplicated:
    - the DOM: <script src>, <link rel=modulepreload> and <link rel=preload as=script>. page.content() is the DOM after
      the page's own scripts ran, so script tags injected at runtime (tag managers, loaders) are included.
    - the HAR: every script the browser actually requested, which also catches import() and fetched modules that never
      appear as a tag.

    internal = same registered domain as the page (a.com, www.a.com, cdn.a.com), external = everything else.
    Entries are absolute URLs; '//cdn/x.js' and relative paths are resolved against the final page URL."""
    name = "javascript"

    def check_if_eligible(self, url: Url) -> bool:
        return True

    def parse(self, url: Url, site_soup: BeautifulSoup, scrape: RawScrapingResult, **kwargs) -> dict:
        base_url = page_base_url(site_soup, scrape.final_url)

        found = []
        for tag in site_soup.select("script[src]"):
            found.append(resolve(base_url, tag["src"]))
        for tag in site_soup.select("link[href]"):
            rel = [r.lower() for r in tag.get("rel", [])]
            if "modulepreload" in rel or ("preload" in rel and tag.get("as", "").lower() == "script"):
                found.append(resolve(base_url, tag["href"]))
        found.extend(self._scripts_from_har(scrape.har_bytes))

        page_domain = registered_domain(scrape.final_url)
        internal, external = [], []
        for script_url in dict.fromkeys(u for u in found if u):  # de-duplicate, keep first-seen order
            (internal if registered_domain(script_url) == page_domain else external).append(script_url)

        return {
            "internal": internal,
            "external": external,
            "inline_count": sum(1 for tag in site_soup.find_all("script") if not tag.has_attr("src")),
        }

    @staticmethod
    def _scripts_from_har(har_bytes: bytes) -> list[str]:
        try:
            entries = json.loads(har_bytes)["log"]["entries"]
        except Exception as e:
            logging.warning(f"Couldn't read HAR for script URLs: {e}")
            return []

        scripts = []
        for entry in entries:
            request_url = entry.get("request", {}).get("url", "")
            if urlsplit(request_url).scheme not in ("http", "https"):
                continue
            mime = (entry.get("response", {}).get("content", {}).get("mimeType") or "").lower()
            path = urlsplit(request_url).path.lower()
            if any(m in mime for m in _JS_MIME_MARKERS) or path.endswith(_JS_EXTENSIONS):
                scripts.append(request_url)
        return scripts
