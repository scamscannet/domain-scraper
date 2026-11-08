import base64
import codecs
import hashlib
import json
from urllib.parse import unquote_to_bytes, urljoin

import httpx
import mmh3
from bs4 import BeautifulSoup

from scraper.models.scraper.scraping_result import RawScrapingResult
from scraper.models.scraper.url import Url
from scraper.modules.base_module import Module
from scraper.modules.helpers import page_base_url, resolve
from log import logging

_FAVICON_TIMEOUT = 10  # seconds
_FAVICON_MAX_BYTES = 1_000_000


def _text(value) -> str | None:
    if value is None:
        return None
    value = " ".join(str(value).split())
    return value or None


class ModuleImplementation(Module):
    """Page metadata in one flat place for quick access: title, descriptions, SEO/robots directives, canonical,
    language, Open Graph / Twitter cards, JSON-LD structured data, icons and the favicon hash.

    favicon.mmh3 is the Shodan-style hash (mmh3 of the base64-encoded bytes), so it can be pivoted on directly
    in Shodan/Censys (http.favicon.hash:<value>) to find other sites using the same icon."""
    name = "metadata"

    def check_if_eligible(self, url: Url) -> bool:
        return True

    def parse(self, url: Url, site_soup: BeautifulSoup, scrape: RawScrapingResult, **kwargs) -> dict:
        base_url = page_base_url(site_soup, scrape.final_url)
        meta = self._meta_tags(site_soup)
        html_tag = site_soup.find("html")
        title_tag = site_soup.find("title")
        canonical = site_soup.find("link", rel="canonical", href=True)
        charset_tag = site_soup.find("meta", charset=True)

        icons = self._icons(site_soup, base_url)

        return {
            "title": _text(title_tag.get_text()) if title_tag else None,
            "description": meta.get("description"),
            "og_description": meta.get("og:description"),
            "twitter_description": meta.get("twitter:description"),
            "keywords": meta.get("keywords"),
            "author": meta.get("author"),
            "generator": meta.get("generator"),
            "robots": meta.get("robots"),
            "googlebot": meta.get("googlebot"),
            "canonical": resolve(base_url, canonical["href"]) if canonical else None,
            "language": _text(html_tag.get("lang")) if html_tag else None,
            "charset": _text(charset_tag["charset"]) if charset_tag else None,
            "viewport": meta.get("viewport"),
            "theme_color": meta.get("theme-color"),
            "open_graph": {k: v for k, v in meta.items() if k.startswith("og:")},
            "twitter": {k: v for k, v in meta.items() if k.startswith("twitter:")},
            "alternates": self._alternates(site_soup, base_url),
            "manifest": self._link_href(site_soup, base_url, "manifest"),
            "icons": icons,
            "favicon": self._favicon(icons, scrape.final_url),
            "structured_data": self._json_ld(site_soup),
            # Every <meta name/property/http-equiv/itemprop> as-is, incl. ones not broken out above
            # (verification tokens, AI/crawler directives like "noai", app links, ...)
            "meta": meta,
        }

    @staticmethod
    def _meta_tags(soup: BeautifulSoup) -> dict:
        meta = {}
        for tag in soup.find_all("meta"):
            key = tag.get("name") or tag.get("property") or tag.get("http-equiv") or tag.get("itemprop")
            content = _text(tag.get("content"))
            if key and content:
                meta.setdefault(key.strip().lower(), content)  # first occurrence wins, like browsers/crawlers
        return meta

    @staticmethod
    def _link_href(soup: BeautifulSoup, base_url: str, rel: str) -> str | None:
        tag = soup.find("link", rel=lambda r: r and rel in [x.lower() for x in (r if isinstance(r, list) else [r])],
                        href=True)
        return resolve(base_url, tag["href"]) if tag else None

    @staticmethod
    def _alternates(soup: BeautifulSoup, base_url: str) -> dict:
        alternates = {}
        for tag in soup.select("link[rel~=alternate][hreflang][href]"):
            href = resolve(base_url, tag["href"])
            if href:
                alternates[tag["hreflang"].strip().lower()] = href
        return alternates

    @staticmethod
    def _icons(soup: BeautifulSoup, base_url: str) -> list[dict]:
        """All declared icons (icon, shortcut icon, apple-touch-icon, mask-icon), in page order."""
        icons = []
        for tag in soup.select("link[rel][href]"):
            rel = " ".join(tag.get("rel", [])).lower()
            if "icon" not in rel:
                continue
            href = tag["href"].strip()
            icons.append({
                "rel": rel,
                "url": href if href.startswith("data:") else resolve(base_url, href),
                "sizes": _text(tag.get("sizes")),
                "type": _text(tag.get("type")),
            })
        return [i for i in icons if i["url"]]

    def _favicon(self, icons: list[dict], final_url: str) -> dict:
        """Hashes of the page's favicon: the first plain 'icon'/'shortcut icon', falling back to /favicon.ico."""
        declared = [i["url"] for i in icons if i["rel"] in ("icon", "shortcut icon")]
        favicon_url = declared[0] if declared else urljoin(final_url, "/favicon.ico")

        data = self._fetch_favicon(favicon_url)
        if not data:
            return {"url": favicon_url, "mmh3": None, "sha256": None}
        return {
            "url": favicon_url if not favicon_url.startswith("data:") else "data:",
            "mmh3": mmh3.hash(codecs.encode(data, "base64")),
            "sha256": hashlib.sha256(data).hexdigest(),
        }

    @staticmethod
    def _fetch_favicon(favicon_url: str) -> bytes | None:
        try:
            if favicon_url.startswith("data:"):
                header, _, payload = favicon_url.partition(",")
                return base64.b64decode(payload) if header.endswith(";base64") else unquote_to_bytes(payload)

            # verify=False: scam sites often have broken certificates, the page itself was loaded anyway
            with httpx.Client(follow_redirects=True, verify=False, timeout=_FAVICON_TIMEOUT) as client:
                r = client.get(favicon_url)
            content_type = r.headers.get("content-type", "").lower()
            # Many servers answer a missing favicon with their HTML 404/home page and status 200
            if r.status_code != 200 or not r.content or "text/html" in content_type:
                return None
            return r.content[:_FAVICON_MAX_BYTES]
        except Exception as e:
            logging.warning(f"Couldn't fetch favicon {favicon_url[:100]}: {e}")
            return None

    @staticmethod
    def _json_ld(soup: BeautifulSoup) -> list:
        """schema.org JSON-LD blocks (Organization, Product, WebSite, ...), parsed. Broken blocks are skipped."""
        blocks = []
        for tag in soup.find_all("script", type=lambda t: t and t.strip().lower() == "application/ld+json"):
            try:
                parsed = json.loads(tag.string or "")
            except (ValueError, TypeError):
                continue
            blocks.extend(parsed if isinstance(parsed, list) else [parsed])
        return blocks
